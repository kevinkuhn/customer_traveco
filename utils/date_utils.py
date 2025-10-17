"""
Date conversion utilities for Traveco data

Handles both Excel serial dates and Swiss DD.MM.YYYY format
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def convert_traveco_date(date_column: pd.Series) -> pd.Series:
    """
    Convert Traveco date column to proper datetime

    Handles:
    1. Excel serial dates (numeric: 45809 = June 1, 2025)
    2. Swiss date format strings (DD.MM.YYYY)
    3. Already converted datetime

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
        # Note: Excel has a bug where it thinks 1900 was a leap year
        excel_epoch = pd.Timestamp('1899-12-30')

        # Convert numeric to datetime
        result = pd.to_datetime(excel_epoch) + pd.to_timedelta(date_column, unit='D')
        return result

    # Otherwise, try Swiss format (DD.MM.YYYY)
    try:
        result = pd.to_datetime(date_column, format='%d.%m.%Y', dayfirst=True)
        return result
    except:
        # Fallback: let pandas infer with dayfirst=True
        result = pd.to_datetime(date_column, dayfirst=True)
        return result


def validate_date_range(dates: pd.Series,
                       expected_min_year: int = 2020,
                       expected_max_year: int = 2026) -> bool:
    """
    Validate that dates are in expected range

    Args:
        dates: Series of dates
        expected_min_year: Minimum expected year
        expected_max_year: Maximum expected year

    Returns:
        True if dates are in valid range
    """
    min_date = dates.min()
    max_date = dates.max()

    if min_date.year < expected_min_year or max_date.year > expected_max_year:
        print(f"⚠️  Warning: Dates outside expected range!")
        print(f"   Found: {min_date.year} to {max_date.year}")
        print(f"   Expected: {expected_min_year} to {expected_max_year}")
        return False

    return True
