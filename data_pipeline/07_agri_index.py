import pandas as pd
import numpy as np
import os
import requests
import zipfile
import io
from statsmodels.tsa.interp.denton import dentonm

def calculate_agri_index():
    print("--- Starting Step 6: Agricultural Output Index ---")
    input_path = 'output/master_dataset_final.csv'
    df = pd.read_csv(input_path)
    
    # Strip column names 
    df.columns = df.columns.str.strip()
    
    crop_map = {
        'Paddy': 'AgriProdIdx_Rice',
        'Tea': 'AgriProdIdx_Tea_leaves',
        'Rubber': 'AgriProdIdx_Natural_rubber_in_primary_forms',
        'Coconut': 'AgriProdIdx_Coconuts_in_shell',
        'Vegetables': 'AgriProdIdx_Vegetables_and_Fruit_Primary'
    }
    
    # Default structural weights
    weights = {'Paddy': 0.35, 'Tea': 0.25, 'Vegetables': 0.25, 'Coconut': 0.10, 'Rubber': 0.05}
    
    try:
        print("Reading authenticated FAOSTAT Value of Production CSV...")
        vap_df = pd.read_csv('../economy/FAOSTAT_data_en_4-8-2026.csv')
        
        # Filter to constant USD
        sl_vap = vap_df[vap_df['Element'].str.contains('constant', case=False, na=False)]
        
        # Filter to recent 8 years to build a stable composite view
        sl_vap = sl_vap[sl_vap['Year'] >= 2015]
        
        items_map = {
            'Rice': 'Paddy',
            'Tea leaves': 'Tea',
            'Natural rubber in primary forms': 'Rubber',
            'Coconuts, in shell': 'Coconut'
        }
        
        dynamic_weights = {}
        for fao_item, mapped_name in items_map.items():
            crop_data = sl_vap[sl_vap['Item'] == fao_item]
            if not crop_data.empty:
                dynamic_weights[mapped_name] = crop_data['Value'].mean()
                
        # Vegetables are split across multiple items in the uploaded csv
        veg_data = sl_vap[sl_vap['Item'].str.contains('vegetable', case=False, na=False)]
        if not veg_data.empty:
            # Sum vegetables together per year, then average
            yearly_veg = veg_data.groupby('Year')['Value'].sum()
            dynamic_weights['Vegetables'] = yearly_veg.mean()
            
        if len(dynamic_weights) == 5:
            total_vap = sum(dynamic_weights.values())
            weights = {k: v / total_vap for k, v in dynamic_weights.items()}
            print(f"Dynamically calculated Crop Weights from FAO: {weights}")
        else:
            print(f"FAO data incomplete ({list(dynamic_weights.keys())}). Using structural fallback weights: {weights}")
            
    except Exception as e:
        print(f"FAO integration exception: {e}. Using fallback weights: {weights}")

    # Calculate index
    print("Applying weights to compute AgriProdIdx_Weighted...")
    weighted_idx = np.zeros(len(df))
    for crop, col_name in crop_map.items():
        w = weights[crop]
        weighted_idx += df[col_name].fillna(0) * w

    df['AgriProdIdx_Weighted'] = weighted_idx

    agri_cols_to_drop = [c for c in df.columns if c.startswith('AgriProdIdx_') and c != 'AgriProdIdx_Weighted']
    df.drop(columns=agri_cols_to_drop, inplace=True)
    
    out_path = 'output/master_dataset_final_weighted.csv'
    df.to_csv(out_path, index=False)
    print(f"Saved new structurally weighted master dataset: {out_path}")
    
    # -------------------------------------------------------------
    # TEMPORAL DISAGGREGATION (Denton-Cholette using Yala/Maha logic)
    # -------------------------------------------------------------
    print("\n--- Temporally Disaggregating Weighted Index ---")
    maha_df = pd.read_csv('../economy/paddy_extent_maha_season.csv')
    yala_df = pd.read_csv('../economy/paddy_extent_yala_season.csv')
    
    maha_data = []
    for _, row in maha_df.iterrows():
        try:
            yr_str = str(row['Year'])
            if '/' in yr_str:
                yr = int(yr_str.split('/')[0]) + 1
                prod = float(str(row['Production (000 Mt)']).replace(',', ''))
                if pd.notna(prod):
                    maha_data.append({'Year': yr, 'Maha_Prod': prod})
        except: pass
    maha_clean = pd.DataFrame(maha_data)
    
    yala_data = []
    for _, row in yala_df.iterrows():
        try:
            yr = int(row['Year'])
            prod = float(str(row['Production (000 Mt)']).replace(',', ''))
            if pd.notna(prod):
                yala_data.append({'Year': yr, 'Yala_Prod': prod})
        except: pass
    yala_clean = pd.DataFrame(yala_data)
    
    years = sorted(list(set(maha_clean['Year']).intersection(set(yala_clean['Year']))))
    q_data = []
    avg_harvest = maha_clean['Maha_Prod'].mean() + yala_clean['Yala_Prod'].mean()
    baseline = avg_harvest * 0.05
    
    for y in years:
        m_val = maha_clean[maha_clean['Year']==y]['Maha_Prod'].values
        m_val = m_val[0] if len(m_val)>0 else baseline
        y_val = yala_clean[yala_clean['Year']==y]['Yala_Prod'].values
        y_val = y_val[0] if len(y_val)>0 else baseline
        
        q_data.append({'Year': y, 'Quarter': 'Q1', 'Indicator': m_val})
        q_data.append({'Year': y, 'Quarter': 'Q2', 'Indicator': baseline})
        q_data.append({'Year': y, 'Quarter': 'Q3', 'Indicator': y_val})
        q_data.append({'Year': y, 'Quarter': 'Q4', 'Indicator': baseline})
        
    ind_df = pd.DataFrame(q_data)
    
    common_years = sorted(list(set(years).intersection(set(df['Year'].dropna()))))
    bench_overlap = df[df['Year'].isin(common_years)]
    ind_overlap = ind_df[ind_df['Year'].isin(common_years)].copy()
    
    # Denton forces Sum(Q) = Annual. For indices, we want Mean(Q) = Annual, so multiply Annual by 4.
    benchmark_series = bench_overlap['AgriProdIdx_Weighted'].values * 4.0
    indicator_series = ind_overlap['Indicator'].values
    
    disaggregated = dentonm(indicator_series, benchmark_series, freq="aq")
    ind_overlap['AgriProdIdx_Weighted_Quarterly'] = disaggregated
    
    # Verify mathematically
    for y in common_years:
        q_sum = ind_overlap[ind_overlap['Year'] == y]['AgriProdIdx_Weighted_Quarterly'].sum()
        a_val = bench_overlap[bench_overlap['Year'] == y]['AgriProdIdx_Weighted'].values[0]
        assert np.isclose(q_sum / 4.0, a_val, rtol=1e-4), f"Mismatch in year {y}!"

    # Cleanup the pure indicator column and save
    ind_overlap = ind_overlap.drop(columns=['Indicator'])
    q_out_path = 'output/quarterly_agricultural_output.csv'
    ind_overlap.to_csv(q_out_path, index=False)
    print(f"Successfully temporally disaggregated weighted index to: {q_out_path}")

if __name__ == "__main__":
    calculate_agri_index()
