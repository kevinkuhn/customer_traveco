"""
Debug script for Sparten mapping issue
Run this from the project root: python debug_sparten_mapping.py
"""

import pandas as pd
import sys
from pathlib import Path

# Ensure we're in the project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.traveco_utils import ConfigLoader, TravecomDataLoader

# Load configuration (adjust path based on where script is run from)
config_path = project_root / 'config' / 'config.yaml'
config = ConfigLoader(str(config_path))

# Fix data paths (config paths are relative to notebooks/, but we're in root)
# Override the raw_path to be relative to project root instead
from pathlib import Path as PathlibPath
data_path = project_root / 'data' / 'swisstransfer_f473fe80-56b4-4ff0-8cbb-1bb5e181450a'

print(f"Looking for data in: {data_path}")
print(f"Exists: {data_path.exists()}\n")

# Load data files directly
print("Loading data files...\n")

order_file = data_path / '20251015 Juni 2025 QS Auftragsanalyse.xlsb'
divisions_file = data_path / '20251015 Sparten.xlsx'

if not order_file.exists():
    print(f"❌ Order file not found: {order_file}")
    print(f"   Please check the path")
    sys.exit(1)

if not divisions_file.exists():
    print(f"❌ Divisions file not found: {divisions_file}")
    print(f"   Please check the path")
    sys.exit(1)

df_orders = pd.read_excel(order_file, engine='pyxlsb')
df_divisions = pd.read_excel(divisions_file)

print(f"✓ Loaded orders: {len(df_orders):,} rows")
print(f"✓ Loaded divisions: {len(df_divisions):,} rows")

print("=" * 80)
print("SPARTEN MAPPING DEBUG")
print("=" * 80)

# 1. Check Divisions file structure
print("\n1. DIVISIONS FILE (Sparten.xlsx)")
print(f"   Shape: {df_divisions.shape}")
print(f"   Columns: {list(df_divisions.columns)}")
print(f"\n   First column (customer number): '{df_divisions.columns[0]}'")
print(f"   Data type: {df_divisions[df_divisions.columns[0]].dtype}")
print(f"\n   Sample values:")
print(df_divisions[[df_divisions.columns[0], 'Sparte']].head(10))

# Get customer column from divisions
divisions_customer_col = df_divisions.columns[0]  # Should be 'Kunden-Nr.'

# 2. Check Orders file structure
print("\n2. ORDERS FILE (Auftragsanalyse.xlsb)")
print(f"   Shape: {df_orders.shape}")

# Find customer column
customer_col_orders = None
for col in ['RKdNr.', 'RKdNr', 'Kunden-Nr.']:
    if col in df_orders.columns:
        customer_col_orders = col
        print(f"   Customer column found: '{col}'")
        break

if customer_col_orders:
    print(f"   Data type: {df_orders[customer_col_orders].dtype}")
    print(f"\n   Sample values:")
    print(df_orders[customer_col_orders].head(10))

    # 3. Check for matches
    print("\n3. MATCHING ANALYSIS")

    # Get unique customers from both
    orders_customers = set(df_orders[customer_col_orders].dropna().unique())
    divisions_customers = set(df_divisions[divisions_customer_col].dropna().unique())

    print(f"   Unique customers in orders: {len(orders_customers):,}")
    print(f"   Unique customers in divisions: {len(divisions_customers):,}")

    # Find overlap
    matching = orders_customers & divisions_customers
    print(f"   Matching customers: {len(matching):,}")

    if len(matching) == 0:
        print("\n   ⚠️  NO MATCHES FOUND!")
        print("\n   Sample customers from orders:")
        sample_orders = list(orders_customers)[:5]
        for c in sample_orders:
            print(f"      {c} (type: {type(c).__name__})")

        print("\n   Sample customers from divisions:")
        sample_divisions = list(divisions_customers)[:5]
        for c in sample_divisions:
            print(f"      {c} (type: {type(c).__name__})")

        # Check if one is numeric and one is string
        orders_sample = df_orders[customer_col_orders].dropna().iloc[0]
        divisions_sample = df_divisions[divisions_customer_col].dropna().iloc[0]

        print(f"\n   Type mismatch check:")
        print(f"      Orders customer: {orders_sample} (type: {type(orders_sample).__name__})")
        print(f"      Divisions customer: {divisions_sample} (type: {type(divisions_sample).__name__})")

        # Check for decimal points
        if pd.api.types.is_numeric_dtype(df_orders[customer_col_orders]):
            print(f"\n   Orders customer is numeric")
            print(f"      Has decimals? {any(df_orders[customer_col_orders].dropna() % 1 != 0)}")

        if pd.api.types.is_numeric_dtype(df_divisions[divisions_customer_col]):
            print(f"\n   Divisions customer is numeric")
            print(f"      Has decimals? {any(df_divisions[divisions_customer_col].dropna() % 1 != 0)}")
    else:
        print(f"\n   ✓ Found {len(matching):,} matching customers")
        print(f"   Sample matches:")
        for c in list(matching)[:5]:
            sparte = df_divisions[df_divisions[divisions_customer_col] == c]['Sparte'].iloc[0]
            print(f"      {c} → {sparte}")

else:
    print("   ✗ Customer column not found in orders!")

# 4. Proposed fix
print("\n" + "=" * 80)
print("RECOMMENDED FIX")
print("=" * 80)

if customer_col_orders:
    orders_type = df_orders[customer_col_orders].dtype
    divisions_type = df_divisions[divisions_customer_col].dtype

    print(f"\nData types:")
    print(f"   Orders: {orders_type}")
    print(f"   Divisions: {divisions_type}")

    if orders_type != divisions_type:
        print(f"\n⚠️  Type mismatch detected!")
        print(f"\nSolution: Convert both to same type before mapping")
        print(f"\nAdd this to notebook 03 before mapping:")
        print(f"""
# Convert both to integer for matching
df['{customer_col_orders}'] = pd.to_numeric(df['{customer_col_orders}'], errors='coerce').astype('Int64')
df_divisions['{divisions_customer_col}'] = pd.to_numeric(df_divisions['{divisions_customer_col}'], errors='coerce').astype('Int64')
        """)
    else:
        print(f"\nTypes match - issue may be with actual values")
        print(f"Check if column names are correct:")
        print(f"   Orders uses: '{customer_col_orders}'")
        print(f"   Divisions uses: '{divisions_customer_col}'")

print("\n" + "=" * 80)
