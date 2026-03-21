import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import json
import os

# Create Visualizations directory if it doesn't exist
os.makedirs('Visualizations', exist_ok=True)

# ---------------------------------------------------------
# Part 1: Plotting and Exporting Visualizations
# ---------------------------------------------------------

# 1. Quarterly Underemployment
quarterly_df = pd.read_csv('labour/finalized_csv/quarterly_underemployment.csv')
quarterly_df['Date'] = pd.to_datetime(quarterly_df['YEAR'].astype(str) + '-' + (quarterly_df['QUARTER'] * 3 - 2).astype(str).str.zfill(2) + '-01')
quarterly_df.set_index('Date', inplace=True)

fig, axes = plt.subplots(3, 1, figsize=(14, 15))
axes[0].plot(quarterly_df.index, quarterly_df['underemp_rate'], color='darkorange', marker='o', linewidth=2)
axes[0].set_title('Sri Lanka Quarterly Underemployment Rate (2015-2024)', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Underemployment Rate (%)')
axes[0].grid(True, linestyle='--', alpha=0.6)

plot_acf(quarterly_df['underemp_rate'].dropna(), ax=axes[1], lags=16, color='darkorange')
axes[1].set_title('Autocorrelation Function (ACF)', fontweight='bold')

plot_pacf(quarterly_df['underemp_rate'].dropna(), ax=axes[2], lags=16, color='darkorange', method='ywm')
axes[2].set_title('Partial Autocorrelation Function (PACF)', fontweight='bold')

plt.tight_layout()
plt.savefig('Visualizations/Quarterly_Underemployment_ACF_PACF.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Master Dataset Macro Trends
master_df = pd.read_csv('DataLoader/master_dataset.csv')
master_df.columns = master_df.columns.str.strip() # Clean column names

# Clean out strings and force numeric
for col in master_df.columns:
    master_df[col] = pd.to_numeric(master_df[col].astype(str).str.replace(',', '').replace(r'^\s*$', np.nan, regex=True), errors='coerce')


fig, ax1 = plt.subplots(figsize=(12, 6))

color = 'tab:red'
ax1.set_xlabel('Year', fontweight='bold')
ax1.set_ylabel('Underemployment Rate (%)', color=color, fontweight='bold')
ax1.plot(master_df['Year'], master_df['Underemployment_Rate'], color=color, marker='o', linewidth=2, label='Underemployment Rate')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle='--', alpha=0.6)

ax2 = ax1.twinx()
color2 = 'tab:blue'
ax2.set_ylabel('Real GDP', color=color2, fontweight='bold')
ax2.plot(master_df['Year'], master_df['Real_GDP'], color=color2, marker='s', linestyle='--', linewidth=2, label='Real GDP')
ax2.tick_params(axis='y', labelcolor=color2)

fig.suptitle('Underemployment Rate vs Contextual Macro Drivers (Yearly)', fontsize=14, fontweight='bold')
fig.tight_layout()
plt.savefig('Visualizations/Underemployment_vs_Macro.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Correlation Heatmap
cols_to_correlate = [
    'Underemployment_Rate', 'Real_GDP', 'GDP_Growth_Rate', 
    'Inflation_Rate', 'Youth_LFPR_15_24', 'Unemployment_Rate',
    'AgriProdIdx_Agriculture', 'Remit_Personal_remittances_received_pct_of_GDP'
]
available_cols = [c for c in cols_to_correlate if c in master_df.columns]
corr_matrix = master_df[available_cols].corr(method='spearman')

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1, square=True,
            linewidths=0.5, cbar_kws={"shrink": .8})
plt.title('Spearman Correlation: Underemployment vs Selected Macro Variables', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('Visualizations/Underemployment_Correlation_Heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# ---------------------------------------------------------
# Part 2: Generating the Notebook
# ---------------------------------------------------------
notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Final Underemployment Presentation & Explanatory Dashboard\n",
    "\n",
    "This notebook provides the foundational diagnostic plots for forecasting **Time-Related and Skill-Based Underemployment**, directly aligning with the research proposal.\n",
    "\n",
    "### Models Targeted in the Flow:\n",
    "- **SARIMA**: Quarter-over-Quarter persistence (ACF/PACF).\n",
    "- **ARDL / VECM & XGBoost / LSTM**: Target Variable vs. Independent Macro Indicators.\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Target Variable: Quarterly Underemployment (2015-2024)\n",
    "Analyzing the quarterly extraction of underemployment to establish stationarity requirements."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "source": [
    "from IPython.display import Image\n",
    "Image(filename='../Visualizations/Quarterly_Underemployment_ACF_PACF.png')"
   ],
   "outputs": []
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Macro-Economic Alignment (Yearly Overlays)\n",
    "Evaluating how major economic movements (e.g., GDP declines) shadow periods of heightened underemployment using the Master Dataset."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "source": [
    "from IPython.display import Image\n",
    "Image(filename='../Visualizations/Underemployment_vs_Macro.png')"
   ],
   "outputs": []
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Global Correlation Matrix\n",
    "Identifying monotonic (Spearman) and continuous (Pearson) relationships for feature selection prior to ML modeling."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "source": [
    "from IPython.display import Image\n",
    "Image(filename='../Visualizations/Underemployment_Correlation_Heatmap.png')"
   ],
   "outputs": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.12"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

with open('Data_Analysis/Final_Underemployment_Dashboard.ipynb', 'w') as f:
    json.dump(notebook_content, f, indent=1)

print("Dashboard created successfully!")
