"""
Traveco Forecasting Utilities

This module provides reusable classes and functions for the Traveco transport
forecasting project. It includes data loading, feature engineering, model training,
and evaluation utilities.

Author: Kevin Kuhn
Date: 2025-10-17
"""

import pandas as pd
import numpy as np
from pathlib import Path
import yaml
from typing import List, Dict, Tuple, Optional
import warnings
from datetime import datetime, timedelta
warnings.filterwarnings('ignore')


class ConfigLoader:
    """Load and manage project configuration"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize configuration loader

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def get(self, key: str, default=None):
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value


class TravecomDataLoader:
    """Load and validate Traveco data files"""

    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Initialize data loader

        Args:
            config: ConfigLoader instance, creates new one if None
        """
        self.config = config if config else ConfigLoader()
        self.data_path = Path(self.config.get('data.raw_path'))

    def load_order_analysis(self) -> pd.DataFrame:
        """
        Load main order analysis file (Auftragsanalyse)

        Returns:
            DataFrame with order data
        """
        file_name = self.config.get('data.order_analysis')
        file_path = self.data_path / file_name

        print(f"Loading order analysis from: {file_path}")

        if not file_path.exists():
            raise FileNotFoundError(f"Order analysis file not found: {file_path}")

        # Read Excel file (xlsb format)
        df = pd.read_excel(file_path, engine='pyxlsb')

        print(f"Loaded {len(df):,} orders with {len(df.columns)} columns")

        return df

    def load_tour_assignments(self) -> pd.DataFrame:
        """
        Load tour assignments file (Tourenaufstellung)

        Returns:
            DataFrame with tour assignment data
        """
        file_name = self.config.get('data.tour_assignments')
        file_path = self.data_path / file_name

        print(f"Loading tour assignments from: {file_path}")

        if not file_path.exists():
            raise FileNotFoundError(f"Tour assignments file not found: {file_path}")

        df = pd.read_excel(file_path)

        print(f"Loaded {len(df):,} tour assignments")

        return df

    def load_divisions(self) -> pd.DataFrame:
        """
        Load customer divisions file (Sparten)

        Returns:
            DataFrame with customer division mapping
        """
        file_name = self.config.get('data.divisions')
        file_path = self.data_path / file_name

        print(f"Loading divisions from: {file_path}")

        if not file_path.exists():
            raise FileNotFoundError(f"Divisions file not found: {file_path}")

        df = pd.read_excel(file_path)

        print(f"Loaded {len(df):,} customer division mappings")

        return df

    def load_all(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Load all data files

        Returns:
            Tuple of (orders, tours, divisions) DataFrames
        """
        orders = self.load_order_analysis()
        tours = self.load_tour_assignments()
        divisions = self.load_divisions()

        return orders, tours, divisions


class TravecomFeatureEngine:
    """Feature engineering utilities for Traveco data"""

    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Initialize feature engine

        Args:
            config: ConfigLoader instance
        """
        self.config = config if config else ConfigLoader()

    def convert_date_column(self, date_column: pd.Series) -> pd.Series:
        """
        Convert date column to proper datetime

        Handles:
        - Excel serial dates (numeric: 45809 = June 1, 2025)
        - ISO format strings (YYYY-MM-DD from CSV)
        - Swiss date format strings (DD.MM.YYYY)
        - Already converted datetime

        Args:
            date_column: Pandas Series with dates

        Returns:
            Series with proper datetime values
        """
        # If already datetime, return as-is
        if pd.api.types.is_datetime64_any_dtype(date_column):
            return date_column

        # Check if it's numeric (Excel serial date)
        if pd.api.types.is_numeric_dtype(date_column):
            # Excel serial dates: days since 1899-12-30 (Excel's epoch)
            excel_epoch = pd.Timestamp('1899-12-30')
            result = pd.to_datetime(excel_epoch) + pd.to_timedelta(date_column, unit='D')
            return result

        # Try different string formats
        # First, try ISO format (from CSV files)
        try:
            result = pd.to_datetime(date_column, format='ISO8601')
            return result
        except:
            pass

        # Try Swiss format (DD.MM.YYYY)
        try:
            result = pd.to_datetime(date_column, format='%d.%m.%Y', dayfirst=True)
            return result
        except:
            pass

        # Final fallback: let pandas infer
        try:
            result = pd.to_datetime(date_column)
            return result
        except Exception as e:
            raise ValueError(f"Could not convert date column. Error: {e}")

    def extract_temporal_features(self, df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """
        Extract temporal features from date column

        Args:
            df: Input DataFrame
            date_column: Name of date column

        Returns:
            DataFrame with added temporal features
        """
        df = df.copy()

        # Convert to datetime using smart conversion
        df[date_column] = self.convert_date_column(df[date_column])

        # Extract temporal features
        temporal_features = self.config.get('features.temporal_features', [
            'year', 'month', 'week', 'quarter', 'day_of_year', 'weekday'
        ])

        if 'year' in temporal_features:
            df['year'] = df[date_column].dt.year

        if 'month' in temporal_features:
            df['month'] = df[date_column].dt.month

        if 'week' in temporal_features:
            df['week'] = df[date_column].dt.isocalendar().week

        if 'quarter' in temporal_features:
            df['quarter'] = df[date_column].dt.quarter

        if 'day_of_year' in temporal_features:
            df['day_of_year'] = df[date_column].dt.dayofyear

        if 'weekday' in temporal_features:
            df['weekday'] = df[date_column].dt.dayofweek

        print(f"Extracted {len(temporal_features)} temporal features")

        return df

    def create_lag_features(self, df: pd.DataFrame, target_col: str,
                           group_col: Optional[str] = None) -> pd.DataFrame:
        """
        Create lag features for time series forecasting

        Args:
            df: Input DataFrame (must be sorted by date)
            target_col: Target column to create lags for
            group_col: Optional grouping column (e.g., 'branch')

        Returns:
            DataFrame with added lag features
        """
        df = df.copy()

        lag_periods = self.config.get('features.lag_periods', [1, 3, 6, 12])

        for lag in lag_periods:
            col_name = f'{target_col}_lag_{lag}'

            if group_col:
                df[col_name] = df.groupby(group_col)[target_col].shift(lag)
            else:
                df[col_name] = df[target_col].shift(lag)

        print(f"Created {len(lag_periods)} lag features for {target_col}")

        return df

    def calculate_time_weights(self, dates: pd.Series, decay_rate: float = 0.3) -> np.ndarray:
        """
        Calculate exponential time decay weights

        Formula: w(t) = exp(-λ * (T - t) / 365)
        where λ is the decay rate

        Args:
            dates: Series of dates
            decay_rate: Decay rate (λ), default 0.3

        Returns:
            Array of weights (normalized)
        """
        dates = pd.to_datetime(dates)

        # Calculate days from most recent date
        days_from_recent = (dates.max() - dates).dt.days

        # Calculate exponential decay weights
        weights = np.exp(-decay_rate * days_from_recent / 365)

        # Normalize weights (sum to 1)
        weights_normalized = weights / weights.sum()

        # Scale back to original length for data duplication
        weights_scaled = weights_normalized * len(weights)

        return weights_scaled

    def identify_carrier_type(self, df: pd.DataFrame, carrier_col: str = 'Nummer.Spedition') -> pd.DataFrame:
        """
        Identify internal vs external carriers

        Args:
            df: Input DataFrame
            carrier_col: Name of carrier number column

        Returns:
            DataFrame with added 'carrier_type' column
        """
        df = df.copy()

        internal_max = self.config.get('filtering.internal_carrier_max', 8889)
        external_min = self.config.get('filtering.external_carrier_min', 9000)

        df['carrier_type'] = df[carrier_col].apply(
            lambda x: 'internal' if pd.notna(x) and x <= internal_max
                     else 'external' if pd.notna(x) and x >= external_min
                     else 'unknown'
        )

        print(f"Carrier type distribution:\n{df['carrier_type'].value_counts()}")

        return df


class TravecomDataCleaner:
    """Data cleaning and validation utilities"""

    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Initialize data cleaner

        Args:
            config: ConfigLoader instance
        """
        self.config = config if config else ConfigLoader()

    def apply_filtering_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply business filtering rules from configuration

        Args:
            df: Input DataFrame

        Returns:
            Filtered DataFrame
        """
        df = df.copy()
        original_len = len(df)

        # Exclude B&T pickup orders (System B&T with empty customer)
        if self.config.get('filtering.exclude_bt_pickups', True):
            # Check if columns exist
            if 'System_id.Auftrag' in df.columns and 'RKdNr' in df.columns:
                mask = ~((df['System_id.Auftrag'] == 'B&T') & (df['RKdNr'].isna()))
                df = df[mask]

                filtered_count = original_len - len(df)
                print(f"Excluded {filtered_count:,} B&T pickup orders")

        return df

    def validate_data(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Validate data and return summary statistics

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with validation results
        """
        validation = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicates': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict()
        }

        print(f"\nData Validation Summary:")
        print(f"  Total rows: {validation['total_rows']:,}")
        print(f"  Total columns: {validation['total_columns']}")
        print(f"  Duplicate rows: {validation['duplicates']:,}")
        print(f"  Columns with missing values: {sum(1 for v in validation['missing_values'].values() if v > 0)}")

        return validation


def evaluate_forecast(actual: np.ndarray, predicted: np.ndarray,
                     metric: str = 'mape') -> float:
    """
    Calculate forecasting evaluation metrics

    Args:
        actual: Actual values
        predicted: Predicted values
        metric: Metric to calculate ('mape', 'rmse', 'mae')

    Returns:
        Metric value
    """
    actual = np.array(actual)
    predicted = np.array(predicted)

    if metric.lower() == 'mape':
        # Mean Absolute Percentage Error
        mask = actual != 0  # Avoid division by zero
        return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100

    elif metric.lower() == 'rmse':
        # Root Mean Square Error
        return np.sqrt(np.mean((actual - predicted) ** 2))

    elif metric.lower() == 'mae':
        # Mean Absolute Error
        return np.mean(np.abs(actual - predicted))

    elif metric.lower() == 'directional_accuracy':
        # Directional Accuracy (trend prediction)
        if len(actual) < 2:
            return np.nan

        actual_direction = np.diff(actual) > 0
        predicted_direction = np.diff(predicted) > 0

        return np.mean(actual_direction == predicted_direction) * 100

    else:
        raise ValueError(f"Unknown metric: {metric}")


def calculate_multiple_metrics(actual: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
    """
    Calculate multiple forecasting metrics at once

    Args:
        actual: Actual values
        predicted: Predicted values

    Returns:
        Dictionary with metric names and values
    """
    metrics = {
        'MAPE': evaluate_forecast(actual, predicted, 'mape'),
        'RMSE': evaluate_forecast(actual, predicted, 'rmse'),
        'MAE': evaluate_forecast(actual, predicted, 'mae'),
        'Directional_Accuracy': evaluate_forecast(actual, predicted, 'directional_accuracy')
    }

    return metrics


def save_processed_data(df: pd.DataFrame, filename: str, config: Optional[ConfigLoader] = None):
    """
    Save processed data to CSV

    Args:
        df: DataFrame to save
        filename: Output filename
        config: ConfigLoader instance
    """
    if config is None:
        config = ConfigLoader()

    output_path = Path(config.get('data.processed_path')) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)
    print(f"Saved {len(df):,} rows to: {output_path}")


def load_processed_data(filename: str, config: Optional[ConfigLoader] = None) -> pd.DataFrame:
    """
    Load processed data from CSV

    Args:
        filename: Input filename
        config: ConfigLoader instance

    Returns:
        Loaded DataFrame
    """
    if config is None:
        config = ConfigLoader()

    input_path = Path(config.get('data.processed_path')) / filename

    if not input_path.exists():
        raise FileNotFoundError(f"Processed data file not found: {input_path}")

    df = pd.read_csv(input_path)
    print(f"Loaded {len(df):,} rows from: {input_path}")

    return df


# Example usage
if __name__ == "__main__":
    print("Traveco Forecasting Utilities")
    print("=" * 50)

    # Test configuration loading
    config = ConfigLoader()
    print(f"\nTarget columns: {config.get('features.target_columns')}")
    print(f"Lag periods: {config.get('features.lag_periods')}")

    # Test data loading
    loader = TravecomDataLoader(config)
    print(f"\nData path: {loader.data_path}")

    print("\nUtilities ready!")
