#!/usr/bin/env python
"""
SHAP Analysis: Economic Features vs Unemployment
This script runs the complete SHAP analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ML and SHAP libraries
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import shap

# Set plotting style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("✓ All libraries imported successfully!")

# ============================================================
# 1. LOAD AND EXPLORE DATA
# ============================================================
print("\n" + "=" * 60)
print("LOAD AND EXPLORE ECONOMIC DATA")
print("=" * 60)

base_path = Path('.').resolve()
labour_path = base_path / 'labour' / 'csv'
economy_path = base_path / 'economy'

# Load unemployment data
unemployment_file = labour_path / 'API_SL.UEM.TOTL.ZS_DS2_en_csv_v2_93.csv'
unemployment_df = pd.read_csv(unemployment_file, skiprows=4)

print(f"\nUnemployment data shape: {unemployment_df.shape}")

# Convert to long format
year_cols = [str(year) for year in range(1990, 2024)]
unemp_long = unemployment_df[['Country Name', 'Indicator Name'] + year_cols].melt(
    id_vars=['Country Name', 'Indicator Name'],
    var_name='Year',
    value_name='Unemployment_Rate'
)
unemp_long['Year'] = pd.to_numeric(unemp_long['Year'], errors='coerce')
unemp_long = unemp_long.dropna(subset=['Unemployment_Rate'])

print(f"Unemployment year range: {unemp_long['Year'].min():.0f} - {unemp_long['Year'].max():.0f}")

# Load economic indicators (FRED format with observation_date)
economic_files = {
    'GDP': 'Gross Domestic Product for Sri Lanka.csv',
    'Inflation': 'Inflation, consumer prices for Sri Lanka.csv',
    'CPI': 'Consumer Price Index for Sri Lanka.csv',
    'GNI': 'Gross National Income for Sri Lanka.csv',
    'Real_GDP': 'Real GDP at Constant National Prices for Sri Lanka.csv',
}

economic_data = {}
print("\nEconomic Indicators Loaded:")
for indicator_name, filename in economic_files.items():
    try:
        filepath = economy_path / filename
        df = pd.read_csv(filepath)
        
        # Handle FRED format with observation_date column
        if 'observation_date' in df.columns:
            df['Year'] = pd.to_datetime(df['observation_date']).dt.year
            value_col = df.columns[1]  # Get the second column (value column)
            
            # Select Year and value, drop NaNs
            df_clean = df[['Year', value_col]].copy().dropna()
            
            # Aggregate by year (mean if multiple values per year)
            df_yearly = df_clean.groupby('Year')[value_col].mean().reset_index()
            df_yearly.columns = ['Year', indicator_name]
            
            economic_data[indicator_name] = df_yearly
            print(f"✓ {indicator_name}: {len(df_yearly)} years")
        else:
            print(f"⚠ {indicator_name}: No observation_date found")
    except Exception as e:
        print(f"✗ {indicator_name}: {str(e)[:40]}")

print(f"\nTotal indicators loaded: {len(economic_data)}")

# ============================================================
# 2. PREPARE FEATURES AND TARGET
# ============================================================
print("\n" + "=" * 60)
print("PREPARE FEATURES AND TARGET")
print("=" * 60)

# Merge all data
print("\nMerging datasets...")
analysis_df = unemp_long[['Year', 'Unemployment_Rate']].copy()
analysis_df = analysis_df.dropna()

print(f"Unemployment: {len(analysis_df)} records, Years: {analysis_df['Year'].min():.0f}-{analysis_df['Year'].max():.0f}")

for indicator_name, df_econ in economic_data.items():
    print(f"  {indicator_name}: {len(df_econ)} records, Years: {df_econ['Year'].min():.0f}-{df_econ['Year'].max():.0f}")
    # Ensure Year columns are both int/float
    analysis_df['Year'] = analysis_df['Year'].astype(int)
    df_econ['Year'] = df_econ['Year'].astype(int)
    analysis_df = analysis_df.merge(df_econ, on='Year', how='inner')
    print(f"    After merge: {len(analysis_df)} records")

print(f"Merged dataset shape: {analysis_df.shape}")
print(f"Years covered: {analysis_df['Year'].min():.0f} - {analysis_df['Year'].max():.0f}")

# Prepare features and target
feature_cols = [col for col in analysis_df.columns if col not in ['Year', 'Unemployment_Rate']]
X = analysis_df[feature_cols].copy()
y = analysis_df['Unemployment_Rate'].copy()

print(f"\nFeatures ({len(feature_cols)}): {feature_cols}")

# Handle missing values and ensure proper types
X = X.fillna(X.mean())
X = X.astype(float)
y = y.astype(float)

print(f"Final dataset shape: {X.shape}")
print(f"Missing values in X: {X.isnull().sum().sum()}")
print(f"Missing values in y: {y.isnull().sum()}")

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

print(f"\nTrain-Test Split:")
print(f"Training: {X_train.shape}, Test: {X_test.shape}")

# ============================================================
# 3. TRAIN MODEL
# ============================================================
print("\n" + "=" * 60)
print("TRAIN PREDICTIVE MODEL")
print("=" * 60)

# Gradient Boosting
gb_model = GradientBoostingRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    random_state=42,
    verbose=0
)
gb_model.fit(X_train, y_train)

y_test_pred_gb = gb_model.predict(X_test)
test_r2_gb = r2_score(y_test, y_test_pred_gb)
test_rmse_gb = np.sqrt(mean_squared_error(y_test, y_test_pred_gb))
test_mae_gb = mean_absolute_error(y_test, y_test_pred_gb)

print(f"\nGradient Boosting Performance:")
print(f"  Test R² Score: {test_r2_gb:.4f}")
print(f"  Test RMSE: {test_rmse_gb:.4f}")
print(f"  Test MAE: {test_mae_gb:.4f}")

# Random Forest
rf_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)

y_test_pred_rf = rf_model.predict(X_test)
test_r2_rf = r2_score(y_test, y_test_pred_rf)

print(f"\nRandom Forest Performance:")
print(f"  Test R² Score: {test_r2_rf:.4f}")

# Select best model
best_model = gb_model if test_r2_gb > test_r2_rf else rf_model
model_name = "Gradient Boosting" if test_r2_gb > test_r2_rf else "Random Forest"
print(f"\n✓ {model_name} selected for SHAP analysis")

# ============================================================
# 4. GENERATE SHAP VALUES
# ============================================================
print("\n" + "=" * 60)
print("GENERATE SHAP EXPLANATIONS")
print("=" * 60)

explainer = shap.TreeExplainer(best_model)
shap_values = explainer.shap_values(X_test)
base_value = explainer.expected_value

# Handle base_value as ndarray
if isinstance(base_value, np.ndarray):
    base_value_scalar = base_value[0] if len(base_value) == 1 else base_value.mean()
else:
    base_value_scalar = base_value

print(f"SHAP values shape: {shap_values.shape}")
print(f"Base value (mean prediction): {base_value_scalar:.4f}")

# Feature importance
mean_abs_shap_values = np.abs(shap_values).mean(axis=0)
feature_importance_df = pd.DataFrame({
    'Feature': feature_cols,
    'Mean_Abs_SHAP': mean_abs_shap_values
}).sort_values('Mean_Abs_SHAP', ascending=False)

print("\nTop Features by SHAP Impact:")
print(feature_importance_df.head(8).to_string(index=False))

# ============================================================
# 5. CREATE VISUALIZATIONS
# ============================================================
print("\n" + "=" * 60)
print("CREATE VISUALIZATIONS")
print("=" * 60)

# Debug SHAP values
print(f"\nSHAP values statistics:")
print(f"  Min: {shap_values.min():.6f}, Max: {shap_values.max():.6f}")
print(f"  Mean: {shap_values.mean():.6f}, Std: {shap_values.std():.6f}")
print(f"  Contains NaN: {np.isnan(shap_values).any()}")
print(f"  Contains Inf: {np.isinf(shap_values).any()}")
print(f"  Number of samples: {shap_values.shape[0]}")

# Summary plots with improved visualization
fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# Plot 1: Enhanced Summary scatter - colored by magnitude
ax1 = fig.add_subplot(gs[0, :])
plt.sca(ax1)

# Flatten SHAP values and feature values for visualization
all_shap_flat = []
all_feature_flat = []
all_colors = []
colors_map = plt.cm.tab10(np.linspace(0, 1, len(feature_cols)))

for i, feature in enumerate(feature_cols):
    shap_vals = shap_values[:, i]
    feature_vals = X_test.iloc[:, i].values
    # Normalize feature values for x-axis positioning
    feature_norm = (feature_vals - feature_vals.min()) / (feature_vals.max() - feature_vals.min() + 1e-8)
    # Add horizontal offset for each feature to separate them
    x_pos = i + feature_norm * 0.8
    ax1.scatter(x_pos, shap_vals, alpha=0.6, s=80, color=colors_map[i], 
               label=feature, edgecolors='k', linewidth=0.3)

ax1.set_xticks(range(len(feature_cols)))
ax1.set_xticklabels(feature_cols, fontsize=11, fontweight='bold')
ax1.set_ylabel('SHAP Value', fontsize=12, fontweight='bold')
ax1.set_title("SHAP Summary: Feature Contributions (Color-coded by Feature)", 
              fontsize=13, fontweight='bold', pad=15)
ax1.grid(alpha=0.3, axis='y')
ax1.axhline(y=0, color='r', linestyle='--', linewidth=2, alpha=0.7, label='SHAP=0')
ax1.legend(loc='upper right', fontsize=10)

# Plot 2: Feature importance bar chart
ax2 = fig.add_subplot(gs[1, 0])
colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(feature_importance_df)))
bars = ax2.barh(range(len(feature_importance_df)), feature_importance_df['Mean_Abs_SHAP'], color=colors)
ax2.set_yticks(range(len(feature_importance_df)))
ax2.set_yticklabels(feature_importance_df['Feature'], fontsize=11, fontweight='bold')
ax2.set_xlabel('Mean |SHAP Value|', fontsize=11, fontweight='bold')
ax2.set_title('Feature Importance by Impact', fontsize=12, fontweight='bold', pad=10)
ax2.grid(axis='x', alpha=0.3)
# Add value labels on bars
for i, (idx, row) in enumerate(feature_importance_df.iterrows()):
    ax2.text(row['Mean_Abs_SHAP'], i, f" {row['Mean_Abs_SHAP']:.4f}", 
            va='center', fontsize=9, fontweight='bold')

# Plot 3: Model performance
ax3 = fig.add_subplot(gs[1, 1])
ax3.axis('off')
metrics_text = f"""
Model Performance:
━━━━━━━━━━━━━━━━━━━━━
Model: {model_name}
Test R² Score: {test_r2_gb:.4f}
Test RMSE: {test_rmse_gb:.4f}%
Test MAE: {test_mae_gb:.4f}%

SHAP Summary:
━━━━━━━━━━━━━━━━━━━━━
Total Samples: {len(X_test)}
Top Feature: {feature_importance_df.iloc[0]['Feature']}
Impact Range: [{shap_values.min():.3f}, {shap_values.max():.3f}]
"""
ax3.text(0.05, 0.95, metrics_text, transform=ax3.transAxes, fontsize=11,
        verticalalignment='top', fontfamily='monospace', 
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Plot 4: Residuals
y_test_pred = best_model.predict(X_test)
residuals = y_test - y_test_pred
ax4 = fig.add_subplot(gs[2, :])
scatter = ax4.scatter(y_test_pred, residuals, alpha=0.6, s=80, c=residuals, 
                     cmap='RdYlGn', edgecolors='k', linewidth=0.5)
ax4.axhline(y=0, color='r', linestyle='--', linewidth=2, label='Perfect Fit')
ax4.set_xlabel('Predicted Unemployment Rate (%)', fontsize=12, fontweight='bold')
ax4.set_ylabel('Residuals', fontsize=12, fontweight='bold')
ax4.set_title('Model Residuals: Prediction Errors', fontsize=13, fontweight='bold', pad=10)
ax4.grid(alpha=0.3)
ax4.legend(fontsize=10)
cbar = plt.colorbar(scatter, ax=ax4, label='Residual Value')

plt.savefig(base_path / 'shap_summary_plots.png', dpi=300, bbox_inches='tight')
print("✓ Saved: shap_summary_plots.png (enhanced with color-coded features)")
plt.close()

# Create individual feature-level plots for better clarity
fig, axes = plt.subplots(len(feature_cols), 2, figsize=(14, 4*len(feature_cols)))
if len(feature_cols) == 1:
    axes = axes.reshape(1, -1)

for idx, feature in enumerate(feature_cols):
    feature_idx = feature_cols.index(feature)
    shap_vals = shap_values[:, feature_idx]
    feature_vals = X_test.iloc[:, feature_idx].values
    
    # Left plot: SHAP value distribution
    ax_left = axes[idx, 0]
    ax_left.hist(shap_vals, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
    ax_left.axvline(shap_vals.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {shap_vals.mean():.4f}')
    ax_left.set_xlabel('SHAP Value', fontsize=11, fontweight='bold')
    ax_left.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax_left.set_title(f'{feature}: SHAP Value Distribution', fontsize=12, fontweight='bold')
    ax_left.grid(alpha=0.3)
    ax_left.legend(fontsize=10)
    
    # Right plot: Feature vs SHAP scatter
    ax_right = axes[idx, 1]
    scatter = ax_right.scatter(feature_vals, shap_vals, alpha=0.6, s=80, 
                              c=shap_vals, cmap='coolwarm', edgecolors='k', linewidth=0.3)
    ax_right.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax_right.set_xlabel(f'{feature} Value', fontsize=11, fontweight='bold')
    ax_right.set_ylabel('SHAP Value', fontsize=11, fontweight='bold')
    ax_right.set_title(f'{feature}: Impact on Prediction', fontsize=12, fontweight='bold')
    ax_right.grid(alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax_right, label='SHAP Value')

plt.tight_layout()
plt.savefig(base_path / 'shap_feature_distributions.png', dpi=300, bbox_inches='tight')
print("✓ Saved: shap_feature_distributions.png (detailed per-feature analysis)")
plt.close()

# Dependence plots for top features
top_features = feature_importance_df.head(4)['Feature'].tolist()
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.ravel()

for plot_idx, feature in enumerate(top_features):
    ax = axes[plot_idx]
    plt.sca(ax)
    shap.dependence_plot(feature, shap_values, X_test, ax=ax, show=False)
    ax.set_title(f"SHAP Dependence: {feature}", fontsize=11, fontweight='bold')
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(base_path / 'shap_dependence_plots.png', dpi=300, bbox_inches='tight')
print("✓ Saved: shap_dependence_plots.png")
plt.close()

# ============================================================
# 6. ANALYSIS RESULTS
# ============================================================
print("\n" + "=" * 60)
print("SHAP ANALYSIS RESULTS")
print("=" * 60)

print("\n📊 FEATURE IMPORTANCE RANKING:")
for rank, (idx, row) in enumerate(feature_importance_df.iterrows(), 1):
    print(f"{rank:2d}. {row['Feature']:25s} | Mean |SHAP|: {row['Mean_Abs_SHAP']:.6f}")

print("\n\n🔍 DETAILED FEATURE INSIGHTS:")
print("-" * 60)

for rank, (idx, row) in enumerate(feature_importance_df.head(5).iterrows(), 1):
    feature = row['Feature']
    feature_idx = feature_cols.index(feature)
    shap_vals_feature = shap_values[:, feature_idx]
    
    positive = np.sum(shap_vals_feature > 0)
    negative = np.sum(shap_vals_feature <= 0)
    
    print(f"\n{rank}. {feature}")
    print(f"   Mean Impact: {row['Mean_Abs_SHAP']:.6f}")
    print(f"   Increases Unemp: {positive} times ({100*positive/len(shap_values):.1f}%)")
    print(f"   Decreases Unemp: {negative} times ({100*negative/len(shap_values):.1f}%)")

print("\n\n📈 MODEL & SHAP PERFORMANCE:")
print("-" * 60)
print(f"Model: {model_name}")
print(f"Test R² Score: {test_r2_gb:.4f}")
print(f"Test RMSE: {test_rmse_gb:.4f}%")
print(f"Test MAE: {test_mae_gb:.4f}%")
print(f"SHAP Explained Variance: {test_r2_gb*100:.1f}%")

print("\n" + "=" * 60)
print("✓ SHAP ANALYSIS COMPLETE!")
print("=" * 60)
print(f"\nOutput files:")
print(f"  - shap_summary_plots.png")
print(f"  - shap_dependence_plots.png")
