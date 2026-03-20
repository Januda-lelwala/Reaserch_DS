# Using Datasets in Different Notebooks

## Overview
You now have **three ways** to access all datasets from any notebook file. Here's how:

---

## **Option 1: Using the Shared `data_loader` Module (RECOMMENDED)** ✅

This is the cleanest and most reusable approach.

### Step 1: Import the module
```python
import sys
from pathlib import Path

# Navigate to parent directory where data_loader.py is located
sys.path.insert(0, str(Path.cwd().parent))

from data_loader import load_all_datasets, get_dataset_info, get_dataset
```

### Step 2: Load all datasets
```python
# Get the base path (one level up from current notebook folder)
base_path = Path.cwd().parent

# Load all datasets
datasets = load_all_datasets(base_path=base_path)

print(f"✓ Loaded {len(datasets)} datasets")
```

### Step 3: Access datasets using any method

#### Method A: Direct access by name
```python
gdp_df = datasets['gross_domestic_product_for_sri_lanka']
inflation_df = datasets['inflation_consumer_prices_for_sri_lanka']
unemployment_df = datasets['unemployment_unemployment_total_pct_of_total_labor']

gdp_df.head()
```

#### Method B: Search for datasets
```python
# Find all unemployment-related datasets
unemployment_datasets = get_dataset(datasets, 'unemployment')

# Find all employment datasets
employment_datasets = get_dataset(datasets, 'employment')
```

#### Method C: Get summary of all datasets
```python
summary = get_dataset_info(datasets)
print(summary)
```

### Complete Example for TimeSeriesForecasting/forecast.ipynb:

```python
# Cell 1: Setup imports
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd().parent))
from data_loader import load_all_datasets, get_dataset_info, get_dataset

# Cell 2: Load datasets
base_path = Path.cwd().parent
datasets = load_all_datasets(base_path=base_path)
print(f"✓ Loaded {len(datasets)} datasets")

# Cell 3: Use the data
gdp = datasets['gross_domestic_product_for_sri_lanka']
unemployment = datasets['unemployment_unemployment_total_pct_of_total_labor']

print(gdp.head())
print(unemployment.head())
```

---

## **Option 2: Using %run Magic Command**

If you prefer not to create a module, you can run the Load_All_Datasets notebook from another notebook:

```python
# In your notebook (e.g., forecast.ipynb)
%run ../Load_All_Datasets.ipynb

# Now all datasets are available as the 'datasets' dictionary
df = datasets['gdp']
```

### Pros:
- Very simple
- No need to create a separate module
- Code is self-contained in Load_All_Datasets.ipynb

### Cons:
- Slower (runs the entire notebook each time)
- Less clean for production code

---

## **Option 3: Copy the Loading Code Directly**

You can copy the loading code directly into your notebook:

```python
import pandas as pd
from pathlib import Path

def load_all_datasets(base_path=None):
    if base_path is None:
        base_path = Path.cwd()
    
    economy_path = base_path / 'economy'
    labour_finalized_path = base_path / 'labour' / 'finalized_csv'
    
    datasets = {}
    
    # ... [copy the rest of the load_all_datasets function from data_loader.py]
    
    return datasets

# Then use it
datasets = load_all_datasets(Path.cwd().parent)
```

### Pros:
- Self-contained
- No dependencies

### Cons:
- Code duplication
- Difficult to maintain

---

## **Step-by-Step Setup Instructions**

### For Any New Notebook:

#### Step 1: Add this to the first cell
```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd().parent))
from data_loader import load_all_datasets, get_dataset_info, get_dataset
```

#### Step 2: Add this to the second cell
```python
# Determine base path based on notebook location
if 'TimeSeriesForecasting' in str(Path.cwd()):
    base_path = Path.cwd().parent
elif 'Data_Analysis' in str(Path.cwd()):
    base_path = Path.cwd().parent
else:
    base_path = Path.cwd()

# Load all datasets
datasets = load_all_datasets(base_path=base_path)
print(f"✓ Loaded {len(datasets)} datasets")
```

#### Step 3: Now use the datasets!
```python
# Access by name
df = datasets['gdp']

# Search
get_dataset(datasets, 'unemployment')

# Get summary
get_dataset_info(datasets)
```

---

## **Notebook Directory Structure**

```
Reaserch_DS/
├── Load_All_Datasets.ipynb          ← Main loading notebook
├── data_loader.py                   ← Shared module
├── economy/                         ← Economy datasets
├── labour/
│   └── finalized_csv/               ← Labour datasets
├── Data_Analysis/
│   ├── notebook1.ipynb
│   └── notebook2.ipynb
└── TimeSeriesForecasting/
    └── forecast.ipynb               ← Can use datasets from here
```

---

## **Available Functions in data_loader.py**

### `load_all_datasets(base_path=None)`
Loads all datasets from economy and labour folders.

**Parameters:**
- `base_path` (str or Path): Base directory containing data folders. Uses current directory if None.

**Returns:**
- `dict`: Dictionary of all loaded datasets

**Example:**
```python
datasets = load_all_datasets(Path.cwd().parent)
```

---

### `get_dataset_info(datasets)`
Gets summary information about all datasets.

**Parameters:**
- `datasets` (dict): Dictionary of datasets

**Returns:**
- `pd.DataFrame`: Summary table with shape, rows, columns, and memory usage

**Example:**
```python
summary = get_dataset_info(datasets)
print(summary)
```

---

### `get_dataset(datasets, search_term)`
Searches for datasets by name.

**Parameters:**
- `datasets` (dict): Dictionary of datasets
- `search_term` (str): Search term (case-insensitive, partial match)

**Returns:**
- `list`: List of matching dataset names

**Example:**
```python
unemployment_dfs = get_dataset(datasets, 'unemployment')
employment_dfs = get_dataset(datasets, 'employment')
```

---

## **All Available Dataset Names**

### Economy Datasets (13)
- `96951c7d_dd12_46a8_af0c_6a6902ca77b2_data`
- `central_government_debt_total_of_gdp_for_sri_lanka`
- `consumer_price_index_for_sri_lanka`
- `faostat_data_en_3_20_2026`
- `gross_domestic_product_for_sri_lanka`
- `gross_domestic_product_per_capita_for_sri_lanka`
- `gross_national_income_for_sri_lanka`
- `inflation_consumer_prices_for_sri_lanka`
- `internet_users_for_sri_lanka`
- `real_gdp_at_constant_national_prices_for_sri_lanka`
- `sri_lankan_rupees_to_u.s._dollar_spot_exchange_rate`
- `metadata_country_api_sl.uem.totl.zs_ds2_en_csv_v2_93`
- `metadata_indicator_api_sl.uem.totl.zs_ds2_en_csv_v2_93`

### Labour Datasets (26+)
**Employment by Sector:**
- `employment_by_sector_employment_in_agriculture_pct`
- `employment_by_sector_employment_in_agriculture_fem`
- `employment_by_sector_employment_in_agriculture_mal`
- ... and more sector/gender combinations

**Unemployment:**
- `unemployment_unemployment_total_pct_of_total_labor`
- `unemployment_unemployment_male_pct_of_male_labor_f`
- `unemployment_unemployment_female_pct_of_female_lab`
- `unemployment_unemployment_youth_total_pct_of_total`
- ... and more

**Labour Force Participation Rate:**
- `labor_force_participation_rate_total_pct_of_total_`
- ... and more by age group and gender

**And many more...**

To see all available datasets, run:
```python
for name in sorted(datasets.keys()):
    print(name)
```

---

## **Troubleshooting**

### Error: "No module named 'data_loader'"
**Solution:** Make sure you've added the parent directory to sys.path:
```python
sys.path.insert(0, str(Path.cwd().parent))
```

### Error: "Failed to load..."
**Solution:** Check that the economy and labour/finalized_csv folders exist in the parent directory.

### Datasets not found
**Solution:** Verify you're using the correct base_path. For notebooks in subdirectories, use `Path.cwd().parent`.

---

## **Quick Copy-Paste Templates**

### For TimeSeriesForecasting/forecast.ipynb:
```python
# Cell 1
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))
from data_loader import load_all_datasets, get_dataset_info, get_dataset

# Cell 2
datasets = load_all_datasets(base_path=Path.cwd().parent)
print(f"✓ Loaded {len(datasets)} datasets")

# Cell 3 - Use your data
df = datasets['gdp']
df.head()
```

### For Data_Analysis/your_notebook.ipynb:
```python
# Cell 1
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))
from data_loader import load_all_datasets, get_dataset_info, get_dataset

# Cell 2
datasets = load_all_datasets(base_path=Path.cwd().parent)

# Cell 3
summary = get_dataset_info(datasets)
display(summary)
```

---

## **Summary**

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Option 1: data_loader module** | Clean, reusable, fast, maintainable | Requires one-time setup | Production code, multiple notebooks |
| **Option 2: %run magic** | Simple, no module needed | Slower, less clean | Quick testing, prototyping |
| **Option 3: Copy code** | Self-contained | Code duplication, hard to maintain | One-off scripts |

**✅ Recommendation:** Use **Option 1** for best practices and maintainability.
