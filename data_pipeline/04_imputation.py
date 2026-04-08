import pandas as pd
import numpy as np
import os
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, KNNImputer

def run_imputation():
    print("--- Starting Imputation Pipeline (Step 4) ---")
    
    input_path = 'output/master_dataset_imputed.csv'
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(input_path)
    
    # Standardize missing
    df.columns = df.columns.str.strip()
    df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    df.replace(r'^\s*\.\.\s*$', np.nan, regex=True, inplace=True)
    df.replace('..', np.nan, inplace=True)
    
    # Isolate numeric
    for col in df.columns:
        if col != 'Underemployment_Note':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    num_cols = [c for c in df.columns if c not in ['Underemployment_Note', 'Year']]
    
    # Base matrix
    base_matrix = df[num_cols].values
    
    # Setup KNN with correct distance weighting
    knn = KNNImputer(n_neighbors=3, weights='distance')
    knn_preds = knn.fit_transform(base_matrix)
    df_knn_preds = pd.DataFrame(knn_preds, columns=num_cols)
    
    # Setup MICE for multiple imputation (m=5 datasets)
    mice_preds_list = []
    for seed in range(5):
        mice = IterativeImputer(max_iter=20, random_state=seed, initial_strategy='median', imputation_order='ascending')
        mice_preds_list.append(pd.DataFrame(mice.fit_transform(base_matrix), columns=num_cols))
    
    audit_logs = []
    
    # Generate 5 discrete imputed CSVs for Rubin's rules
    for seed in range(5):
        df_imputed = df.copy()
        for col in num_cols:
            is_null = df[col].isnull()
            if is_null.any():
                null_indices = df[df[col].isnull()].index.tolist()
                
                for idx in null_indices:
                    yr = int(df.at[idx, 'Year'])
                    
                    # Check isolation
                    prev_null = (idx - 1) in null_indices
                    next_null = (idx + 1) in null_indices
                    is_isolated = not (prev_null or next_null)
                    
                    method = "KNN" if is_isolated else "MICE"
                    reason = "isolated gap" if is_isolated else "block/edge gap"
                    
                    # Take from KNN or from this specific MICE seed
                    imputed_val = df_knn_preds.at[idx, col] if is_isolated else mice_preds_list[seed].at[idx, col]
                    df_imputed.at[idx, col] = imputed_val
                    
                    # Only log audit bounds during the first seed to avoid duplicates
                    if seed == 0:
                        adj = []
                        if idx > 0 and pd.notnull(df.at[idx-1, col]):
                            adj.append(df.at[idx-1, col])
                        if idx < len(df)-1 and pd.notnull(df.at[idx+1, col]):
                            adj.append(df.at[idx+1, col])
                        
                        if len(adj) == 2:
                            rg = f"[{min(adj):.2f} - {max(adj):.2f}]"
                        elif len(adj) == 1:
                            rg = f"~{adj[0]:.2f}"
                        else:
                            rg = "No adjacent valid data"
                            
                        audit_logs.append({
                            "Variable": col,
                            "Time Period (Year)": yr,
                            "Imputed Value (Seed 0)": round(imputed_val, 4),
                            "Adjacent Range": rg,
                            "Method": method,
                            "Reason": reason,
                            "Model": "Both (Annual & Quarterly)"
                        })

        # Save each multiple-imputed dataset separately
        out_name = os.path.join(output_dir, f"master_dataset_imputed_seed{seed}.csv")
        df_imputed.to_csv(out_name, index=False)
        print(f"Exported Multiple Imputation Dataset (Seed {seed}): {out_name}")

    # Pool the point estimates according to Rubin's rule for point estimate (average of m datasets)
    df_pooled = df.copy()
    for col in num_cols:
        is_null = df[col].isnull()
        if is_null.any():
            null_indices = df[df[col].isnull()].index.tolist()
            for idx in null_indices:
                prev_null = (idx - 1) in null_indices
                next_null = (idx + 1) in null_indices
                is_isolated = not (prev_null or next_null)
                
                if is_isolated:
                    df_pooled.at[idx, col] = df_knn_preds.at[idx, col]
                else:
                    sum_val = sum(mice_preds_list[seed].at[idx, col] for seed in range(5))
                    df_pooled.at[idx, col] = sum_val / 5.0
                    
    final_out_name = os.path.join(output_dir, "master_dataset_final.csv")
    df_pooled.to_csv(final_out_name, index=False)
    print(f"Exported Pooled Final Imputation Dataset: {final_out_name}")

    # Generate Markdown
    md_content = "# Data Imputation Audit Report\n\n"
    md_content += "This audit details the computationally generated fills for missing data within the master dataset.\n"
    md_content += "Notice: MICE was generated across $m=5$ datasets. Point estimate values below reflect **Seed 0** for illustrational purposes. Proper standard errors should pool across all 5 exported databases.\n\n"
    
    if audit_logs:
        md_content += "| Variable | Year | Method | Reason | Seed 0 Imputed Value | Plausible Bounds | Used In |\n"
        md_content += "|----------|------|--------|--------|----------------------|------------------|---------|\n"
        for log in audit_logs:
            md_content += f"| `{log['Variable']}` | **{log['Time Period (Year)']}** | {log['Method']} | *{log['Reason']}* | {log['Imputed Value (Seed 0)']} | {log['Adjacent Range']} | {log['Model']} |\n"
    
    with open('output/imputation_audit.md', 'w') as f:
        f.write(md_content)
        
    print(f"Generated Audit report for {len(audit_logs)} missing values.")

if __name__ == "__main__":
    run_imputation()
