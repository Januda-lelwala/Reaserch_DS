import pandas as pd
import numpy as np
from pathlib import Path
import glob

def process_year(file_path):
    print(f"Processing {file_path}")
    df = pd.read_csv(file_path, low_memory=False)
    df.columns = [str(c).upper() for c in df.columns]
    
    def get_col(names):
        for n in names:
            if n.upper() in df.columns:
                return n.upper()
        return None
        
    year_col = get_col(['YEAR'])
    month_col = get_col(['MONTH'])
    weight_col = get_col(['ANNUALFACTOR_25PERCENT', 'ANNUAL_FACTOR', 'WEIGHT'])
    hrs_col = get_col(['Q40B', 'Q40_B', 'Q40', 'HOURS_WORKED'])
    
    if not (year_col and month_col and hrs_col):
        return None

    # Handle numeric conversions
    df[month_col] = pd.to_numeric(df[month_col], errors='coerce')
    df[hrs_col] = pd.to_numeric(df[hrs_col].astype(str).str.replace(r'^\s*$', 'NaN', regex=True), errors='coerce')
    if weight_col:
        df[weight_col] = pd.to_numeric(df[weight_col].astype(str).str.replace(r'^\s*$', 'NaN', regex=True), errors='coerce')
    else:
        df['WEIGHT'] = 1.0
        weight_col = 'WEIGHT'
        
    df['QUARTER'] = ((df[month_col] - 1) // 3) + 1
    
    employed = df[df[hrs_col] > 0].copy()
    if len(employed) == 0:
        return None
        
    employed['is_underemployed'] = employed[hrs_col] < 40
    
    # Calculate weighted stats
    def calc_stats(group):
        total_w = group[weight_col].sum()
        under_w = group.loc[group['is_underemployed'], weight_col].sum()
        return pd.Series({
            'total_employed_weighted': total_w,
            'underemployed_weighted': under_w,
            'underemp_rate': (under_w / total_w) * 100 if total_w > 0 else 0,
            'sample_size': len(group)
        })

    summary = employed.groupby(['YEAR', 'QUARTER']).apply(calc_stats).reset_index()
    return summary

all_summaries = []
files = glob.glob('labour/csv/*_25_Percent_Datafile_Out.csv') + glob.glob('labour/csv/LFS-*-25-Percent-Data-Without-Computer*.csv')

for f in sorted(files):
    try:
        res = process_year(f)
        if res is not None:
            all_summaries.append(res)
    except Exception as e:
        print(f"Error processing {f}: {e}")

if all_summaries:
    final = pd.concat(all_summaries, ignore_index=True)
    # Remove NaN quarters
    final = final.dropna(subset=['QUARTER'])
    final['QUARTER'] = final['QUARTER'].astype(int)
    final['YEAR'] = final['YEAR'].astype(int)
    final = final.sort_values(['YEAR', 'QUARTER'])
    print(final)
    final.to_csv('extraction/weighted_quarterly_underemployment.csv', index=False)
