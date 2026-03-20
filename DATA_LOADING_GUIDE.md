# Data Loading Solution - Sri Lanka Economic & Labour Data

## Overview
Created a complete data loading system that automatically discovers and loads all datasets from:
- **Economy folder**: 13 datasets loaded
- **Labour/finalized_csv folder**: 26+ datasets loaded

**Total: 39+ datasets loaded with appropriate variable names**

---

## Files Created

### 1. **Load_All_Datasets.ipynb** (Jupyter Notebook)
- **Location**: `/Users/janudax/Computer_Science/Uom stuff/Reaserch_DS/Load_All_Datasets.ipynb`
- **Purpose**: Main interactive notebook for loading all datasets
- **Features**:
  - Auto-discovery of all CSV files
  - Intelligent variable naming based on filenames and folder structure
  - Summary table showing all loaded datasets with shapes and memory usage
  - Quick reference list for accessing datasets

**How to Use**:
```python
# Run the notebook to load all datasets into the 'datasets' dictionary
# Then access any dataset:
df = datasets['inflation_consumer_prices_for_sri_lanka']
df = datasets['unemployment_total']
df = datasets['employment_by_sector_employment_in_agriculture_pct']
```

### 2. **load_all_data.py** (Python Script)
- **Location**: `/Users/janudax/Computer_Science/Uom stuff/Reaserch_DS/load_all_data.py`
- **Purpose**: Standalone Python script for data loading
- **Usage**: Run from terminal to load and display all datasets
```bash
./myenv/bin/python load_all_data.py
```

### 3. **load_datasets.py** (Alternative Loading Script)
- **Location**: `/Users/janudax/Computer_Science/Uom stuff/Reaserch_DS/load_datasets.py`
- **Purpose**: Initial comprehensive loader with detailed logging

---

## Loaded Datasets

### Economy Datasets (13 total)
1. `96951c7d_dd12_46a8_af0c_6a6902ca77b2_data` - Agricultural employment data
2. `central_government_debt_total_of_gdp_for_sri_lanka` - Government debt as % of GDP
3. `consumer_price_index_for_sri_lanka` - CPI
4. `faostat_data_en_3_20_2026` - FAO agricultural data
5. `gross_domestic_product_for_sri_lanka` - GDP
6. `gross_domestic_product_per_capita_for_sri_lanka` - GDP per capita
7. `gross_national_income_for_sri_lanka` - GNI
8. `inflation_consumer_prices_for_sri_lanka` - Inflation rates
9. `internet_users_for_sri_lanka` - Internet usage
10. `metadata_country_api_sl.uem.totl.zs_ds2_en_csv_v2_93` - Metadata
11. `metadata_indicator_api_sl.uem.totl.zs_ds2_en_csv_v2_93` - Metadata
12. `real_gdp_at_constant_national_prices_for_sri_lanka` - Real GDP
13. `sri_lankan_rupees_to_u.s._dollar_spot_exchange_rate` - Exchange rates

### Labour Datasets (26+ total)

**Employment by Sector** (9 datasets):
- Employment in agriculture/industry/services (% of total, male, female)

**Employment-to-Population Ratio** (12 datasets):
- Various age groups and gender breakdowns

**Labour Force Participation Rate** (13 datasets):
- Total, male, female for different age groups
- Both modeled and national estimates

**Labour Force** (3 datasets):
- Labour force total, male, female

**Part-Time Employment** (3 datasets):
- Total, male, female part-time employment

**Unemployment** (12 datasets):
- Multiple measures including youth unemployment
- National and modeled ILO estimates

**Other Labour Data** (3 datasets):
- Underemployment by sector and gender
- Employment by gender

---

## Quick Start Guide

### Option 1: Use the Jupyter Notebook (Recommended)
```python
# Just run the notebook and all datasets will be loaded into the 'datasets' dictionary
import pandas as pd

# Access any dataset
df = datasets['gdp']
print(df.head())

# List all available datasets
print(list(datasets.keys()))
```

### Option 2: Use the Python Script
```bash
cd "/Users/janudax/Computer_Science/Uom stuff/Reaserch_DS"
./myenv/bin/python load_all_data.py
```

### Option 3: Import the Loading Module
```python
# Create a custom script that imports the logic from load_all_data.py
import sys
sys.path.append(str(Path.cwd()))
from load_all_data import datasets, clean_var_name
```

---

## Variable Naming Convention

All dataset variable names follow this pattern:
1. **Economy datasets**: Direct filename conversion
   - Example: `Inflation, consumer prices for Sri Lanka.csv` → `inflation_consumer_prices_for_sri_lanka`

2. **Labour datasets**: Folder prefix + filename
   - Example: File `Unemployment, total (...).csv` in `Unemployment_(%)_sl_indicators/` folder
   - Result: `unemployment_unemployment_total_pct_of_total_labor`

### Name Cleaning Rules:
- Remove `.csv` extension
- Convert spaces to underscores
- Remove special characters like (), %
- Convert to lowercase
- Remove duplicate underscores
- Limit to 60 characters

---

## Dataset Access Examples

```python
# Economic data
gdp_df = datasets['gross_domestic_product_for_sri_lanka']
inflation_df = datasets['inflation_consumer_prices_for_sri_lanka']
exchange_rate_df = datasets['sri_lankan_rupees_to_u.s._dollar_spot_exchange_rate']

# Labour data
unemployment_df = datasets['unemployment_unemployment_total_pct_of_total_labor']
lfpr_df = datasets['labor_force_participation_rate_total_pct_of_total_']
employment_sector_df = datasets['employment_by_sector_employment_in_agriculture_pct']

# Check available datasets
for name in sorted(datasets.keys()):
    print(f"{name}: {datasets[name].shape}")
```

---

## Features

✅ **Auto-Discovery**: Automatically finds all CSV files  
✅ **Intelligent Naming**: Creates meaningful variable names from filenames  
✅ **Error Handling**: Gracefully handles read errors  
✅ **Summary Statistics**: Shows shape, rows, columns, and memory usage  
✅ **Easy Access**: All datasets stored in a single dictionary  
✅ **Memory Efficient**: Reports total memory usage  
✅ **Organized Output**: Displays results organized by folder/category  

---

## Notes

- One metadata file failed to load due to tokenization error (API_SL.UEM.TOTL.ZS_DS2_en_csv_v2_93.csv)
- All other 39+ datasets loaded successfully
- Memory usage displayed in the notebook summary
- Datasets can be exported or saved to new formats as needed

---

## Integration with Other Notebooks

The `datasets` dictionary persists after loading and can be used in any subsequent cells or imported into other notebooks:

```python
# In another notebook
%run Load_All_Datasets.ipynb

# Now access the datasets
df = datasets['gdp']
```

---

Created: March 20, 2026
