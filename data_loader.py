"""
Shared Data Loading Module
Loads all datasets from economy and labour/finalized_csv folders
"""

import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def clean_var_name(filename, folder_name=''):
    """Convert filename to a clean, readable variable name"""
    name = filename.replace('.csv', '')
    if folder_name:
        name = folder_name + '_' + name
    
    name = name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
    name = name.replace('%', 'pct').replace(',', '').replace('  ', '_')
    name = name.lstrip('/')
    
    while '__' in name:
        name = name.replace('__', '_')
    
    name = name.strip('_').lower()
    if len(name) > 60:
        name = name[:60]
    
    return name


def load_all_datasets(base_path=None):
    """
    Load all datasets from economy and labour/finalized_csv folders
    
    Parameters:
    -----------
    base_path : str or Path, optional
        Base path to the data folders. If None, uses current working directory.
    
    Returns:
    --------
    dict : Dictionary containing all loaded datasets
    """
    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path)
    
    economy_path = base_path / 'economy'
    labour_finalized_path = base_path / 'labour' / 'finalized_csv'
    
    datasets = {}
    
    # Load economy datasets
    if economy_path.exists():
        for csv_file in sorted(economy_path.glob('*.csv')):
            try:
                var_name = clean_var_name(csv_file.name)
                datasets[var_name] = pd.read_csv(csv_file)
            except Exception as e:
                print(f"Warning: Failed to load {csv_file.name}: {str(e)[:50]}")
    
    # Load labour datasets
    if labour_finalized_path.exists():
        for subdir in sorted(labour_finalized_path.iterdir()):
            if subdir.is_dir():
                folder_label = subdir.name.replace('_sl_indicators', '').replace('(%)_', '').replace('(%)', '')
                folder_label = folder_label.replace('_', ' ').strip()
                
                for csv_file in sorted(subdir.glob('*.csv')):
                    try:
                        var_name = clean_var_name(csv_file.stem, folder_label.lower().replace(' ', '_'))
                        datasets[var_name] = pd.read_csv(csv_file)
                    except Exception as e:
                        print(f"Warning: Failed to load {csv_file.name}: {str(e)[:50]}")
    
    return datasets


def get_dataset_info(datasets):
    """
    Get summary information about all loaded datasets
    
    Parameters:
    -----------
    datasets : dict
        Dictionary of datasets
    
    Returns:
    --------
    pd.DataFrame : Summary table with dataset info
    """
    summary_data = []
    for name in sorted(datasets.keys()):
        df = datasets[name]
        summary_data.append({
            'Variable Name': name,
            'Shape': str(df.shape),
            'Rows': df.shape[0],
            'Columns': df.shape[1],
            'Memory (MB)': round(df.memory_usage(deep=True).sum() / 1024**2, 2)
        })
    
    return pd.DataFrame(summary_data)


# Convenience function for quick access
def get_dataset(datasets, search_term):
    """
    Search for a dataset by name
    
    Parameters:
    -----------
    datasets : dict
        Dictionary of datasets
    search_term : str
        Search term (case-insensitive partial match)
    
    Returns:
    --------
    list : Matching dataset names
    """
    search_term = search_term.lower()
    matches = [name for name in datasets.keys() if search_term in name]
    
    if matches:
        for match in matches:
            print(f"✓ {match} - Shape: {datasets[match].shape}")
        return matches
    else:
        print(f"✗ No datasets found matching '{search_term}'")
        return []
