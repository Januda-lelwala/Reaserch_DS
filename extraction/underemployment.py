import pandas as pd
import numpy as np
from pathlib import Path
import glob
import re

def process_year(file_path):
    print(f"Processing {file_path}")
    df = pd.read_csv(file_path, low_memory=False)
    
    # Standardize column names to uppercase to handle differences between years
    df.columns = [str(c).upper() for c in df.columns]
    
    # Function to get column ignoring case
    def get_col(names):
        for n in names:
            if n.upper() in df.columns:
                return n.upper()
        return None
        
    year_col = get_col(['YEAR'])
    month_col = get_col(['MONTH'])
    weight_col = get_col(['AnnualFactor_25Percent', 'ANNUALFACTOR_25PERCENT', 'ANNUAL_FACTOR', 'WEIGHT'])
    
    # In Sri Lanka LFS, q40a (Q40A or Q40_A) is usually total hours usually worked
    # q40b (Q40B or Q40_B) is actual hours worked during reference week
    # q42 or q43 might ask about willingness to work more hours
    hrs_col = get_col(['Q40B', 'Q40_B', 'Q40', 'HOURS_WORKED'])
    
    if not (year_col and month_col and hrs_col):
        print(f"Missing essential columns in {file_path}")
        return None
        
    # Convert hours to numeric
    # It might contain spaces or strings
    df[hrs_col] = pd.to_numeric(df[hrs_col].replace(r'^\s*$', np.nan, regex=True), errors='coerce')
    
    # Calculate Quarter
    df['QUARTER'] = ((pd.to_numeric(df[month_col], errors='coerce') - 1) // 3) + 1
    
    # Filter only those who worked (hours > 0)
    employed = df[df[hrs_col] > 0].copy()
    
    if len(employed) == 0:
        return None
        
    # Example logic: underemployed if actual hours < 40
    employed['is_underemployed'] = employed[hrs_col] < 40
    
    # Just a simple count for now to verify
    summary = employed.groupby(['YEAR', 'QUARTER']).agg(
        total_employed=('is_underemployed', 'count'),
        underemployed=('is_underemployed', 'sum')
    ).reset_index()
    
    summary['underemp_rate'] = (summary['underemployed'] / summary['total_employed']) * 100
    
    return summary

all_summaries = []
files = glob.glob('labour/csv/*_25_Percent_Datafile_Out.csv') + \
        glob.glob('labour/csv/LFS-*-25-Percent-Data-Without-Computer*.csv')

for f in sorted(files):
    try:
        res = process_year(f)
        if res is not None:
            all_summaries.append(res)
    except Exception as e:
        print(f"Error processing {f}: {e}")

if all_summaries:
    final = pd.concat(all_summaries, ignore_index=True)
    final = final.sort_values(['YEAR', 'QUARTER'])
    print(final)
    final.to_csv('extraction/quarterly_underemployment.csv', index=False)
