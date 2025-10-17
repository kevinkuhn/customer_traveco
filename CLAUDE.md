# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **transport logistics forecasting project** for Travecom, a Swiss transport/logistics company. The project implements advanced time series forecasting to predict 2025 transport demand using multiple ensemble models.

**Client**: Travecom (Switzerland)
**Objective**: Predict 2025 monthly transport metrics (revenue, external drivers, personnel costs) using historical order data
**Stage**: Analytical prototype with strategic recommendations for productionization

## Technology Stack

- **Language**: Python
- **Primary Environment**: Jupyter Notebooks
- **Key Libraries**:
  - **Forecasting**: Prophet, SARIMAX (statsmodels), XGBoost
  - **ML**: scikit-learn (RandomForest, GradientBoostingRegressor)
  - **Data**: pandas, numpy, scipy
  - **Visualization**: Plotly (interactive dashboards)
  - **Utilities**: tqdm, warnings

## Repository Structure

```
customer_traveco/
├── notebooks/
│   └── Forecast.ipynb           # Main forecasting implementation (424 lines)
├── data/
│   └── swisstransfer_*/         # Excel files with transport order data
│       ├── 20251015 Sparten.xlsx                    # Product categories
│       ├── 20251015 QS Tourenaufstellung Juni 2025.xlsx  # Tour assignments
│       └── 20251015 Juni 2025 QS Auftragsanalyse.xlsb   # Order analysis (23.6 MB)
└── information/
    ├── recommendation.md        # Strategic forecasting recommendations
    └── mail.pdf                 # Client communication
```

## Development Commands

### Running the Forecasting Notebooks

This is a Jupyter-based project. To work with the code:

```bash
# Start Jupyter from project root
jupyter notebook

# Or use Jupyter Lab
jupyter lab

# Navigate to notebooks/
```

### Recommended Notebook Structure

For building this project step-by-step, create the following notebook sequence:

#### Phase 1: Data Understanding

**`01_data_loading_and_exploration.ipynb`**
- Load three Excel files (Auftragsanalyse, Tourenaufstellung, Sparten)
- Initial data exploration (shape, dtypes, head/tail, info)
- Understand column mappings from data dictionary
- Check for missing values and data completeness
- Apply filtering rules (exclude B&T pickup orders)
- **Output**: Raw data loaded and understood

**`02_data_cleaning_and_validation.ipynb`**
- Handle missing values (decide on strategy: drop, fill, interpolate)
- Validate business rules from data dictionary
- Data type conversions (dates, numeric fields)
- Outlier detection and handling
- Create clean dataset with documentation of changes
- **Output**: `data/processed/clean_orders.csv`

#### Phase 2: Feature Engineering

**`03_feature_engineering.ipynb`**
- Extract temporal features (year, month, week, quarter, day_of_year, weekday)
- Calculate distances (use Column CU: Distanz_BE, not CV)
- Identify pickup vs delivery (Tilde column)
- Map customers to divisions (Sparten)
- Add carrier type flag (internal vs external based on carrier number)
- Calculate time decay weights
- Create lag features (1, 3, 6, 12 months)
- **Output**: `data/processed/features_engineered.csv`

**`04_aggregation_and_targets.ipynb`**
- Monthly aggregation by branch
- Calculate target variables: revenue, external_drivers, personnel_costs
- Create train/validation split (e.g., hold out 2024 for validation)
- Verify aggregation logic against business expectations
- **Output**: `data/processed/monthly_aggregated.csv`

#### Phase 3: Exploratory Analysis

**`05_exploratory_data_analysis.ipynb`**
- Time series visualization (trends, seasonality)
- Seasonal decomposition (trend, seasonal, residual)
- Branch-level analysis (which branches have strongest seasonality?)
- Customer division analysis (Sparten patterns)
- Carrier analysis (internal vs external trends)
- Tour type analysis (FD, SH, Normal, etc.)
- Correlation analysis between features
- Identify Swiss-specific patterns (holidays, school vacations)
- **Output**: Insights document, key visualizations saved

#### Phase 4: Baseline Models

**`06_baseline_models.ipynb`**
- Current method: Linear averaging (yearly average / 12)
- Simple moving average (3-month, 6-month, 12-month)
- Naive forecast (last year same month)
- Seasonal naive (repeat last year's pattern)
- Calculate baseline metrics (MAPE, RMSE)
- **Output**: Baseline performance benchmarks

#### Phase 5: Advanced Models - Seasonality Focus

**`07_model_a_prophet.ipynb`**
- Prophet implementation with custom seasonalities
- Hyperparameter tuning (changepoint_prior_scale, seasonality parameters)
- Add Swiss holidays
- Test quarterly (91.25 days) and monthly (30.5 days) seasonalities
- Cross-validation using TimeSeriesSplit
- Generate 2025 forecasts
- **Output**: Prophet model, forecasts, performance metrics

**`08_model_a_sarimax.ipynb`**
- SARIMAX implementation
- Order selection (test different p,d,q and P,D,Q,s combinations)
- Diagnostic plots (residuals, ACF, PACF)
- Stationarity tests (ADF test)
- Generate 2025 forecasts
- **Output**: SARIMAX model, forecasts, performance metrics

**`09_model_a_xgboost.ipynb`**
- XGBoost with temporal features
- Feature importance analysis
- Hyperparameter tuning (n_estimators, max_depth, learning_rate)
- Cross-validation
- Generate 2025 forecasts
- **Output**: XGBoost model, forecasts, feature importance, metrics

#### Phase 6: Advanced Models - Time Decay Focus

**`10_model_b_weighted_prophet.ipynb`**
- Prophet with exponential time decay weighting
- Test different decay rates (λ = 0.2, 0.3, 0.4, 0.5)
- Implement weighted loss via data duplication or custom loss
- Compare against standard Prophet
- Generate 2025 forecasts
- **Output**: Weighted Prophet model, forecasts, metrics

**`11_model_b_time_weighted_ensemble.ipynb`**
- Year-level RandomForest ensemble
- Calculate year weights: `exp(-0.5 * (2025 - year))`
- Weighted voting mechanism
- Test different ensemble strategies
- Generate 2025 forecasts
- **Output**: Ensemble model, forecasts, metrics

#### Phase 7: Model Selection and Evaluation

**`12_model_comparison.ipynb`**
- Load all model forecasts
- Calculate comprehensive metrics:
  - MAPE (overall and by month)
  - RMSE
  - Seasonal MAPE (by quarter)
  - Directional accuracy
  - Forecast bias
- Statistical significance tests (Diebold-Mariano test)
- Model ranking by metric
- Ensemble of best models (weighted average)
- **Output**: Model comparison table, recommendation

**`13_model_diagnostics.ipynb`**
- Residual analysis for all models
- Forecast error patterns
- Branch-specific performance
- Month-specific performance
- Identify where models fail
- **Output**: Diagnostic insights, model strengths/weaknesses

#### Phase 8: Production Forecasts

**`14_final_forecast_2025.ipynb`**
- Retrain best model(s) on full dataset
- Generate final 2025 monthly forecasts
- Create confidence intervals
- Branch-level forecasts
- Division-level forecasts (Sparten)
- **Output**: `results/forecast_2025.csv`

**`15_visualization_and_reporting.ipynb`**
- Interactive Plotly dashboards
- Historical vs forecast comparison
- Model A vs Model B comparison
- Current method vs new approach
- Branch-level dashboards
- Export charts for presentation
- Create executive summary
- **Output**: `results/dashboard.html`, presentation slides

#### Supporting Files

**`utils/traveco_utils.py`** (Python module)
```python
# Reusable functions for the project
class TravecomDataLoader:
    """Load and validate Traveco data files"""

class TravecomFeatureEngine:
    """Feature engineering utilities"""

class TravecomForecaster:
    """Unified forecasting interface"""

def calculate_time_weights(dates, decay_rate=0.3):
    """Calculate exponential time decay weights"""

def evaluate_forecast(actual, predicted):
    """Calculate forecasting metrics"""
```

**`config/config.yaml`** (Configuration file)
```yaml
data:
  raw_path: "data/swisstransfer_*/"
  processed_path: "data/processed/"

features:
  lag_periods: [1, 3, 6, 12]
  target_columns: ["revenue", "external_drivers", "personnel_costs"]

models:
  prophet:
    yearly_seasonality: true
    seasonality_mode: "multiplicative"
    changepoint_prior_scale: 0.05

  sarimax:
    order: [2, 1, 2]
    seasonal_order: [1, 1, 1, 12]

  xgboost:
    n_estimators: 200
    max_depth: 6
    learning_rate: 0.05

  time_decay:
    decay_rate: 0.3
    year_decay: 0.5
```

### Notebook Execution Order

Execute notebooks in sequence for a complete workflow:

```bash
# Phase 1: Data Understanding
jupyter notebook notebooks/01_data_loading_and_exploration.ipynb
jupyter notebook notebooks/02_data_cleaning_and_validation.ipynb

# Phase 2: Feature Engineering
jupyter notebook notebooks/03_feature_engineering.ipynb
jupyter notebook notebooks/04_aggregation_and_targets.ipynb

# Phase 3: EDA
jupyter notebook notebooks/05_exploratory_data_analysis.ipynb

# Phase 4-6: Modeling
jupyter notebook notebooks/06_baseline_models.ipynb
jupyter notebook notebooks/07_model_a_prophet.ipynb
# ... continue with other model notebooks

# Phase 7-8: Evaluation and Production
jupyter notebook notebooks/12_model_comparison.ipynb
jupyter notebook notebooks/14_final_forecast_2025.ipynb
jupyter notebook notebooks/15_visualization_and_reporting.ipynb
```

### Python Environment Setup

No `requirements.txt` exists yet. Install dependencies manually:

```bash
pip install pandas numpy prophet scikit-learn xgboost statsmodels plotly tqdm scipy
```

Or if using the workspace-level Pipenv (from parent `/Users/kk/dev/`):

```bash
cd /Users/kk/dev
pipenv shell
cd customer_traveco
jupyter notebook
```

### Working with the Data

**Data Loading Pattern** (expected in notebooks):
```python
import pandas as pd

# Load order analysis data
data = pd.read_excel('data/swisstransfer_*/20251015 Juni 2025 QS Auftragsanalyse.xlsb')

# Expected schema:
# - tour_start_date (datetime)
# - auftragsschein_id (order ID)
# - branch (branch identifier)
# - revenue (numeric)
# - external_drivers (count)
# - personnel_costs (numeric)
```

## Data Dictionary

The following detailed field explanations are provided by Traveco (see `information/mail.pdf`). These define the structure of files in `data/swisstransfer_*/`:

### 1. Data Filtering Rules

**Exclude B&T Pickup Orders** (not relevant for analysis):
- Filter: System B&T (Column CW) = "B&T" AND Customer (RKDNr Column L) = empty
- These are internal pickup orders that should not be included in forecasting

### 2. Transport Type Classifications

**Column Mappings**:
- **Column K**: `Auftragsart` (Order type)
- **Column AU**: `Lieferart 2.0` (Delivery type)
- **Column CW**: `System_id.Auftrag` (System ID)
- **Column AR**: `Text für Auswertung` (Description)
- **Column AS**: `∑ Einheiten` (Total units)
- **Column AT**: `∑ Frachtpfl. Gewicht` (Freight weight)

**Transport Categories**:

| Order Type | Delivery Type | System | Units | Weight | Description |
|------------|---------------|--------|-------|--------|-------------|
| - | **B&T Fossil** | B&T | x100 ist lt | - | Fossil fuel delivery |
| - | **B&T Holzpellets** | B&T | x100 ist kg | - | Wood pellets delivery |
| - | **Flüssigtransporte** | TRP | - | ist kg | Liquid transport |
| - | **Lager Auftrag** | TRP | - | - | Warehouse orders (not relevant) |
| - | **Losetransporte** | TRP | - | ist kg | Bulk transport (do not use) |
| Leergut | **Palettentransporte** | TRP | EH alle TM in SBB Kg | kg | Empty pallet returns |
| Lieferung | **Palettentransporte** | TRP | EH alle TM in SBB Kg | kg | Pallet delivery |
| Retoure/Abholung | **Palettentransporte** | TRP | EH alle TM in SBB Kg | kg | Pallet return/pickup |

### 3. Carrier Identification (Spediteure)

**Columns**:
- **Column BC**: `Nummer.Spedition` (Carrier number)
- **Column BD**: `Name.Spedition` (Carrier name)

**Carrier Code Ranges**:
- **1 - 8889**: TRAVECO internal carriers
- **9000+**: External carriers (Fremdfahrer)

**TRAVECO Internal Carriers**:

| Code | Name |
|------|------|
| 1100 | B&T Winterthur |
| 1200 | B&T Landquart |
| 1500 | BZ Intermodal / Rail |
| 1600 | B&T Puidoux |
| 1900 | BZ Sierre |
| 3000 | BZ Oberbipp |
| 4000 | BZ Winterthur |
| 5000 | BZ Nebikon |
| 6000 | BZ Herzogenbuchsee |
| 6040-6042 | BZ/B&T Puidoux |
| 7000 | BZ Landquart |

**External Carriers (examples)**:

| Code | Name |
|------|------|
| 9000 | Benz Steffen Transporte |
| 9004 | Bachmann AG Transporte Schweiz |
| 9013 | Blättler Transport AG |

### 4. Pickup vs Delivery Identification

**Column CY**: `Tilde.Auftrag` (Tilde flag)
- **"Ja" (Yes)**: Pickup order (Vorholung) - marked with `~` in order number
- **"Nein" (No)**: Delivery order (Auslieferung)

**Distance Calculation**:
- **Use Column CU** (`Distanz_BE.Auftrag`): Distance from loading location to unloading location
- **Do NOT use Column CV** (`Distanz_VE.Auftrag`): Sender to receiver distance

**Cross-Docking Example**:
When an order routes through a cross-dock facility (e.g., Sursee), the order is split:
- Pickup leg: Order number ends with `~001` (Tilde = "Ja")
- Delivery leg: Same order number without tilde (Tilde = "Nein")

Example from data:
```
Hauptauftrag: RAM0081584480_0
  - Pickup:   RAM0081584480~001 | Date: 02.06.2025 | Tour: 565058 | HOCHDORF → Sursee
  - Delivery: RAM0081584480     | Date: 03.06.2025 | Tour: 567567 | Sursee → GEBENSTORF
```

### 5. Customer Billing Information

**Columns**:
- **Column L**: `RKdNr` (Customer billing number)
- **Column M**: `RKdArt` (Customer type: R = regular)
- **Column N**: `RKdName` (Customer name)
- **Column O**: `RKdOrt` (Customer city)

**Product Divisions (Sparten)**:
Customers are categorized into divisions. See separate file: `20251015 Sparten.xlsx` for mapping of customer numbers to divisions.

Example:
```
RKdNr: 946200 | Type: R | Name: Volg Konsumwaren AG | City: Winterthur
```

### 6. Loading and Unloading Locations

**Loading Location (Beladestelle)**:
- **Column AD**: `Nummer.Beladestelle` (Loading location ID)
- **Column AE**: `Name.Beladestelle` (Loading location name)
- **Column AF**: `Beladestelle Name 2` (Alternative name)
- **Column AG**: `Land.Beladestelle` (Country code: CH)
- **Column AH**: `Strasse.Beladestelle` (Street)
- **Column AI**: `PLZ.Beladestelle` (Postal code)
- **Column AJ**: `Ort.Beladestelle` (City)

**Unloading Location (Entladestelle)**:
- **Column AK**: `Nummer.Entladestelle` (Unloading location ID)
- Followed by similar fields (Name, Address, etc.)

Example:
```
Loading:   0020 | RAMSEIER Suisse AG | CH | Niffel | 6280 | HOCHDORF
Unloading: 5000 | BZ Sursee | TRAVECO Transporte AG | CH | Obstfeldstrasse 7 | 6210 | Sursee
```

### 7. Sender and Receiver Information

**Sender (Versender)**:
- **Column P**: `Nummer.Versender` (Sender ID)
- **Column Q**: `Name.Versender` (Sender name)
- **Column R**: `Versender Name 2` (Alternative name)
- **Column S**: `Strasse.Versender` (Street)
- **Column T**: `Land.Versender` (Country)
- **Column U**: `Ort.Versender` (City)
- **Column V**: `PLZ.Versender` (Postal code)

**Receiver (Empfänger)**:
- **Column W**: `Nummer.Empfänger` (Receiver ID)
- **Column X**: `Name.Empfänger` (Receiver name)
- Plus corresponding address fields

Example:
```
Sender:   0020 | RAMSEIER Suisse AG | Niffel | CH | HOCHDORF | 6280
Receiver: RAM0000205639 | LANDI Laden Gebenstorf | Hornblick 3 | CH | GEBENSTORF | 5412
```

### 8. Dispatch Locations (Dispostellen)

**Column H**: `Id.Dispostelle` (Dispatch location ID)

**TRAVECO Dispatch Centers**:

| ID | Name |
|----|------|
| 1_TRP_Lahr | Lahr dispatch center |
| 4_TRP_Winterthur | Winterthur dispatch |
| 5_TRP_Sursee | Sursee dispatch |
| 6_TRP_Herzogenbuchsee (EP) | Herzogenbuchsee (endpoint) |
| 7_TRP_Landquart | Landquart dispatch |
| 14_TRP_Oberbipp | Oberbipp dispatch |
| 15_TRP_Intermodal | Intermodal rail |
| 16_TRP_Herzogenbuchsee (DP) | Herzogenbuchsee (dispatch point) |
| 18_TRP_Puidoux (DP) | Puidoux dispatch |
| 19_TRP_Sierre | Sierre dispatch |
| 1000_TRP_Lager Nebikon | Nebikon warehouse |
| 90_TRP_Lager Hägendorf | Hägendorf warehouse |
| 99_TRP_Fakturierung | Billing/invoicing |

**B&T Dispatch Centers**:

| ID | Name |
|----|------|
| 1_B&T_1100 Ohringen | Ohringen B&T |
| 2_B&T_1200 Landquart | Landquart B&T |
| 6_B&T_1600 Puidoux | Puidoux B&T |
| 7_B&T_1150 OH-PELO | OH-PELO B&T |

### 9. Tour Information

**Columns**:
- **Column D**: `Datum.Tour` (Tour date)
- **Column E**: `Nummer.Tour` (Tour number)
- **Column F**: `Tour Bezeichnung` (Tour description)
- **Column CT**: `TourTyp.Tour` (Tour type code)

**Tour Type Codes**:

| Code | Description |
|------|-------------|
| **FD** | Fahrdienstleistung (Driving service) |
| **SH** | Subunternehmer (Subcontractor) |
| **Normal** | Standard tour |
| **TS** | Tour special |
| **GE** | Gebiet (Regional) |
| **Direktlieferung** | Direct delivery |
| **Bahn Vor-/Nachlauf** | Rail pre/post-haul |
| **Intermodal Bahn beladen** | Intermodal rail loaded |
| **Intermodal Bahn leer** | Intermodal rail empty |

Example:
```
Date: 01.06.2025 | Tour: 557265 | Name: 2130 Kuoni Samedan | Type: FD
```

### 10. PraCar System Data (Tour Costs)

**Columns**:
- **Column A**: Tour date (duplicate of Column D)
- **Column B**: Tour ID
- **Column K**: `Fahrzeug KM` (Vehicle kilometers from PraCar system)
- **Column L**: `Minuten Kosten` (Minute costs from PraCar)
- **Column T**: `Soll KM der Tour` (Target/planned kilometers)
- **Column V**: `IST Zeit PraCar` (Actual time from PraCar)
- **Column AB**: `Tour End (errechnet)` (Calculated tour end time)

**Note**: PraCar is Traveco's internal fleet management system that tracks actual vehicle performance and costs.

### Data Files Summary

**Three main files provided by Traveco**:

1. **`20251015 Juni 2025 QS Auftragsanalyse.xlsb`** (23.6 MB)
   - Main order analysis data
   - Contains all columns described above
   - Full historical order data for forecasting

2. **`20251015 QS Tourenaufstellung Juni 2025.xlsx`** (2.85 MB)
   - Tour assignments for June 2025
   - Links orders to specific tours and vehicles

3. **`20251015 Sparten.xlsx`** (28 KB)
   - Customer division/category mapping
   - Maps customer billing numbers to product divisions

**File Access**:
- Delivered via SwissTransfer (password protected)
- Available for 7 days from October 15, 2025
- Stored in: `K:\Administration\20_Projekte_und_Pflichtenhefte\Fakturierung\Saison Zahlen 2025` (internal Traveco path)

## Forecasting Architecture

### Core Class: `TravecomForecaster`

The main forecasting system is implemented as a single stateful class in `Forecast.ipynb`:

```python
forecaster = TravecomForecaster(
    data=df,
    target_columns=['revenue', 'external_drivers', 'personnel_costs']
)

# Standard workflow:
monthly_data = forecaster.prepare_data()          # 1. Prepare with temporal features
forecasts = forecaster.generate_forecasts()       # 2. Train all models
fig = forecaster.visualize_forecasts()            # 3. Interactive visualization
fig.show()
```

### Dual Model Strategy

The system implements **two complementary model families**:

#### Model A: Seasonality-Focused
Captures transport industry seasonal patterns (summer peaks, quarterly cycles):

1. **Prophet** (primary)
   - Multiplicative seasonality mode
   - Custom seasonalities: quarterly (91.25 days), monthly (30.5 days)
   - Swiss holiday awareness
   - Config: `yearly_seasonality=True, seasonality_mode='multiplicative', changepoint_prior_scale=0.05`

2. **SARIMAX** (statistical baseline)
   - ARIMA(2,1,2) with seasonal (1,1,1,12) for monthly patterns
   - Branch-specific effects via exogenous variables

3. **XGBoost** (non-linear patterns)
   - 200 estimators, depth=6, learning_rate=0.05
   - Lag features: [1, 3, 6, 12] months
   - Temporal features: month, quarter, week, day_of_year, weekday

#### Model B: Seasonality + Time Decay
Emphasizes recent data relevance (addresses structural market changes):

1. **Weighted Prophet**
   - Exponential decay: `w(t) = exp(-λ * (T - t))` where λ = 0.3-0.5
   - Recent data weighted ~2x older data
   - More responsive changepoint detection (prior_scale=0.1)

2. **Time-Weighted Ensemble**
   - Year-level RandomForest models with exponential year weights
   - Weighted voting: `year_weight = exp(-0.5 * (2025 - year))`

### Data Processing Pipeline

**Key Methods**:

```python
# 1. Temporal Feature Engineering
forecaster.prepare_data()
# Extracts: year, month, week, quarter, day_of_year, weekday
# Aggregates: Monthly by branch
# Calculates: revenue, external_drivers, personnel_costs sums

# 2. Time Decay Weighting
weights = forecaster.calculate_time_weights(dates, decay_rate=0.3)
# Formula: exp(-decay_rate * days_from_recent / 365)

# 3. Model Training (automated)
forecaster.generate_forecasts()
# Trains all 6 models sequentially with progress bar

# 4. Visualization
forecaster.visualize_forecasts()
# Returns Plotly figure with 3 subplots (one per target metric)
```

## Model Configuration Reference

### Prophet Parameters
```python
Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,      # Monthly aggregation makes this irrelevant
    daily_seasonality=False,       # Same reason
    seasonality_mode='multiplicative',  # Percentage-based seasonality
    changepoint_prior_scale=0.05   # 0.1 for weighted variant (more responsive)
)

# Custom seasonalities
model.add_seasonality(name='quarterly', period=91.25, fourier_order=5)
model.add_seasonality(name='monthly', period=30.5, fourier_order=10)
```

### SARIMAX Parameters
```python
SARIMAX(
    ts_data,
    order=(2, 1, 2),              # ARIMA order: AR(2), I(1), MA(2)
    seasonal_order=(1, 1, 1, 12), # Seasonal: SAR(1), SI(1), SMA(1), period=12
    enforce_stationarity=False,
    enforce_invertibility=False
)
```

### XGBoost Parameters
```python
xgb.XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    random_state=42
)
```

### Time Decay Parameters
```python
decay_rate = 0.3        # λ in exponential decay formula
year_decay = 0.5        # For year-level ensemble weighting
```

## Validation and Metrics

### Validation Strategy
```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
# Recommended: Hold out 2024 data for validation
```

### Performance Metrics
```python
forecaster.calculate_accuracy_metrics(actual_2025_data)
```

Returns metrics for each target:
- **MAPE** (Mean Absolute Percentage Error) - Primary metric
- **RMSE** (Root Mean Square Error) - Outlier sensitivity
- **Seasonal MAPE** - Month/quarter-specific accuracy
- **Directional Accuracy** - Trend prediction correctness

## Domain Context

### Swiss Transport Industry Specifics
- **LSVA tax**: Heavy vehicle tax affecting costs
- **School vacations**: Demand seasonality driver
- **Cooled goods**: Summer peak seasonality
- **Regional economics**: Branch-specific demand patterns

### Data Scale
- **~1.2M records/year** mentioned in strategic recommendations
- **Monthly aggregation** reduces dimensionality for forecasting
- **Branch-level granularity** maintained for spatial patterns

## Strategic Recommendations

The `information/recommendation.md` file provides implementation guidance:

- **Primary Model**: Prophet for interpretability (board-level presentation)
- **Validation**: Time series CV with 2024 holdout
- **Feature Engineering**: Swiss holidays, weather, fuel prices, LSVA changes
- **Timeline**: 8-week implementation (prep → modeling → validation → presentation)

## Working with This Codebase

### To Modify Models

1. **Adjust seasonality**: Edit Prophet `add_seasonality()` calls in `model_a_prophet()` and `model_b_weighted_prophet()`
2. **Change decay rates**: Modify `decay_rate` parameter in `calculate_time_weights()` and `model_b_weighted_prophet()`
3. **Add lag features**: Update lag list `[1, 3, 6, 12]` in `model_a_xgboost()`
4. **Change target metrics**: Pass different `target_columns` to `TravecomForecaster.__init__()`

### To Add New Models

Add methods following naming pattern:
```python
def model_a_your_model(self, target_col):
    """Model A: Your model description"""
    # Train and return model + forecast
    return model, forecast

def model_b_your_model(self, target_col):
    """Model B: Your model with time decay"""
    # Train with time weighting
    return model, forecast
```

Then integrate into `generate_forecasts()` method.

### To Extend Visualization

Modify `visualize_forecasts()` to add new traces:
```python
fig.add_trace(
    go.Scatter(
        x=your_forecast_dates,
        y=your_forecast_values,
        name='Your Model Name',
        line=dict(color='purple', dash='dash')
    ),
    row=idx, col=1
)
```

## Current Project Status

- **Stage**: Analytical prototype with complete forecasting framework
- **Repository**: `git@github.com:kevinkuhn/customer_traveco.git`
- **Branch**: main (no commits yet - newly created)
- **Missing**: Production deployment code, Docker setup, tests, requirements.txt

**Next Steps for Productionization**:
1. Create `requirements.txt` with pinned versions
2. Extract `TravecomForecaster` into standalone Python module
3. Add data validation and error handling
4. Implement unit tests for model methods
5. Create CLI or API wrapper (FastAPI) for forecast generation
6. Add logging and monitoring
7. Document data preprocessing expectations
