import pandas as pd
import re
from pathlib import Path

# Define base paths
base_path = Path(__file__).parent
economy_path = base_path / 'economy'
labour_finalized_path = base_path / 'labour' / 'finalized_csv'

print("=" * 80)
print("DATA LOADING MODULE - Sri Lanka Economic & Labour Data")
print("=" * 80)
print()

# Dictionary to store all loaded datasets
datasets = {}

def clean_var_name(filename, folder_name=''):
    """Convert filename to a clean variable name"""
    # Remove .csv extension
    name = filename.replace('.csv', '')
    
    # Add folder context if provided
    if folder_name:
        name = folder_name + '_' + name
    
    # Replace problematic characters
    name = name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
    name = name.replace('%', 'pct').replace(',', '').replace('  ', '_')
    
    # Remove multiple underscores
    while '__' in name:
        name = name.replace('__', '_')
    
    # Remove leading/trailing underscores
    name = name.strip('_').lower()
    
    # Limit length
    if len(name) > 50:
        name = name[:50]
    
    return name

# ============================================================================
# ECONOMY DATASETS
# ============================================================================
print("📊 ECONOMY DATASETS")
print("-" * 80)

if economy_path.exists():
    for csv_file in sorted(economy_path.glob('*.csv')):
        try:
            var_name = clean_var_name(csv_file.name)
            datasets[var_name] = pd.read_csv(csv_file)
            print(f"  ✓ {var_name:40} {str(datasets[var_name].shape):20}")
        except Exception as e:
            print(f"  ✗ {csv_file.name:40} ERROR: {str(e)[:30]}")

print()

# ============================================================================
# LABOUR DATASETS - AUTO DISCOVERY
# ============================================================================
print("💼 LABOUR DATASETS (from finalized_csv)")
print("-" * 80)

if labour_finalized_path.exists():
    # Walk through all subdirectories and load CSV files
    for subdir in sorted(labour_finalized_path.iterdir()):
        if subdir.is_dir():
            # Clean folder name for variable naming
            folder_label = subdir.name.replace('_sl_indicators', '').replace('(%)_', '').replace('(%)', '')
            folder_label = folder_label.replace('_', ' ').strip()
            
            csv_files = list(subdir.glob('*.csv'))
            if csv_files:
                print(f"\n  {folder_label}")
                print(f"  {'-' * 60}")
                
                for csv_file in sorted(csv_files):
                    try:
                        var_name = clean_var_name(csv_file.stem, folder_label.lower().replace(' ', '_'))
                        datasets[var_name] = pd.read_csv(csv_file)
                        print(f"    ✓ {var_name:35} {str(datasets[var_name].shape):20}")
                    except Exception as e:
                        print(f"    ✗ {csv_file.name:35} ERROR: {str(e)[:25]}")

print()
print("=" * 80)
print(f"✅ LOADING COMPLETE - {len(datasets)} datasets loaded")
print("=" * 80)
print()
print("Available Variables (sorted):")
print("-" * 80)
for i, name in enumerate(sorted(datasets.keys()), 1):
    print(f"{i:2}. datasets['{name}']")

print()
print("=" * 80)
