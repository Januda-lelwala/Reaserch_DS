import pandas as pd
import os
from pathlib import Path

# Define base paths
base_path = Path(__file__).parent
economy_path = base_path / 'economy'
labour_finalized_path = base_path / 'labour' / 'finalized_csv'

# Dictionary to store all loaded datasets
datasets = {}

# ============================================================================
# Load Economy Datasets
# ============================================================================
print("Loading Economy Datasets...")
print("=" * 70)

economy_files = {
    'Unemployment_Total.csv': 'unemployment_total',
    'Inflation, consumer prices for Sri Lanka.csv': 'inflation_consumer_prices',
    'Consumer Price Index for Sri Lanka.csv': 'cpi',
    'Gross Domestic Product for Sri Lanka.csv': 'gdp',
    'Gross Domestic Product Per Capita for Sri Lanka.csv': 'gdp_per_capita',
    'Gross National Income for Sri Lanka.csv': 'gni',
    'Real GDP at Constant National Prices for Sri Lanka.csv': 'real_gdp_constant_prices',
    'Central government debt, total (_ of GDP) for Sri Lanka.csv': 'central_govt_debt_pct_gdp',
    'Internet users for Sri Lanka.csv': 'internet_users',
    'Sri Lankan Rupees to U.S. Dollar Spot Exchange Rate.csv': 'exchange_rate_lkr_usd',
    'FAOSTAT_data_en_3-20-2026.csv': 'fao_agricultural_data',
    '96951c7d-dd12-46a8-af0c-6a6902ca77b2_Data.csv': 'agriculture_employment_data',
}

for filename, var_name in economy_files.items():
    filepath = economy_path / filename
    if filepath.exists():
        try:
            datasets[var_name] = pd.read_csv(filepath)
            print(f"✓ Loaded {var_name:40} | Shape: {datasets[var_name].shape}")
        except Exception as e:
            print(f"✗ Failed to load {var_name:40} | Error: {str(e)[:50]}")
    else:
        print(f"⊙ File not found: {filename}")

print()

# ============================================================================
# Load Labour Datasets from finalized_csv subdirectories
# ============================================================================
print("Loading Labour Datasets from finalized_csv...")
print("=" * 70)

# Map folder names to variable name prefixes
labour_mapping = {
    'Employment_by_sector_(%)_sl_indicators': 'employment_by_sector',
    'Employment_to_population_ratio_(%)_sl_indicators': 'employment_to_population_ratio',
    'Labor_force_participation_rate,_total_(% of total population ages 15-64)_(modeled ILO estimate)_sl_indicators': 'lfpr_total',
    'Labor_force,_total_sl_indicators': 'labor_force_total',
    'Part_time_employment,_total_(% of total employment)_sl_indicators': 'part_time_employment',
    'Unemployment_(%)_sl_indicators': 'unemployment_rate',
    'sl_labour_csv': 'sl_labour_data',
    'tru-csv': 'tru_data',
}

# Find and load all CSV files from labour subdirectories
labour_files = []
for folder_name, var_prefix in labour_mapping.items():
    folder_path = labour_finalized_path / folder_name
    if folder_path.exists():
        csv_files = list(folder_path.glob('*.csv'))
        for csv_file in csv_files:
            try:
                # Create variable name from folder prefix and file name
                file_stem = csv_file.stem.replace(' ', '_').replace('-', '_').lower()
                # Clean up the variable name
                var_name = f"{var_prefix}_{file_stem}"
                # Limit variable name length and remove duplicates
                var_name = var_name[:80]
                
                datasets[var_name] = pd.read_csv(csv_file)
                print(f"✓ Loaded {var_name:55} | Shape: {datasets[var_name].shape}")
            except Exception as e:
                print(f"✗ Failed to load {csv_file.name:50} | Error: {str(e)[:40]}")

print()

# ============================================================================
# Summary
# ============================================================================
print("=" * 70)
print(f"LOADING COMPLETE")
print(f"Total datasets loaded: {len(datasets)}")
print()
print("Available datasets:")
print("-" * 70)
for i, (name, df) in enumerate(sorted(datasets.items()), 1):
    print(f"{i:2}. {name:55} | Shape: {str(df.shape):15}")

print()
print("=" * 70)
print("Access datasets using the 'datasets' dictionary:")
print("  Example: datasets['gdp'].head()")
print()

# Display all variable names for easy reference
print("All variable names for quick access:")
print("-" * 70)
for i, name in enumerate(sorted(datasets.keys()), 1):
    if i % 3 == 0:
        print(f"{name}")
    else:
        print(f"{name:30}", end=" ")
if len(datasets) % 3 != 0:
    print()
