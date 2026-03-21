import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set global style
plt.style.use('default')
sns.set_theme(style="whitegrid")

# Create Visualizations directory if it doesn't exist
os.makedirs('Visualizations', exist_ok=True)

# Colors for consistency
COLOR_MALE = 'royalblue'
COLOR_FEMALE = 'crimson'
COLOR_NORMAL = 'teal'
COLOR_CRISIS = 'darkorange'

# Load Datasets
quarterly_df = pd.read_csv('labour/finalized_csv/quarterly_underemployment.csv')
quarterly_df['Date'] = pd.to_datetime(quarterly_df['YEAR'].astype(str) + '-' + (quarterly_df['QUARTER'] * 3 - 2).astype(str).str.zfill(2) + '-01')
quarterly_df.set_index('Date', inplace=True)

master_df = pd.read_csv('DataLoader/master_dataset.csv')
master_df.columns = master_df.columns.str.strip() # Clean column names
for col in master_df.columns:
    master_df[col] = pd.to_numeric(master_df[col].astype(str).str.replace(',', '').replace(r'^\s*$', np.nan, regex=True), errors='coerce')

# ---------------------------------------------------------
# 1. The Gender Gap Over Time
# ---------------------------------------------------------
print("Generating Gender Gap Trends...")
fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(master_df['Year'], master_df['Underemployment_Male'], color=COLOR_MALE, marker='o', linewidth=2.5, label='Male Underemployment (% )')
ax.plot(master_df['Year'], master_df['Underemployment_Female'], color=COLOR_FEMALE, marker='o', linewidth=2.5, label='Female Underemployment (% )')

# Fill the gap between them to highlight disparity
ax.fill_between(master_df['Year'], master_df['Underemployment_Male'], master_df['Underemployment_Female'], 
                where=(master_df['Underemployment_Female'] > master_df['Underemployment_Male']),
                interpolate=True, alpha=0.15, color=COLOR_FEMALE, label='Gender Gap (Female Higher)')

ax.set_title('Sri Lanka Underemployment Rate: Male vs Female (2015-2024)', fontsize=14, fontweight='bold')
ax.set_xlabel('Year', fontweight='bold')
ax.set_ylabel('Underemployment Rate (%)', fontweight='bold')
ax.legend(loc='upper right')
ax.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('Visualizations/Gender_Gap_Underemployment.png', dpi=300, bbox_inches='tight')
plt.close()

# ---------------------------------------------------------
# 2. Quarterly Seasonality Boxplots
# ---------------------------------------------------------
print("Generating Quarterly Seasonality Boxplots...")
fig, ax = plt.subplots(figsize=(10, 6))

sns.boxplot(x='QUARTER', y='underemp_rate', data=quarterly_df, ax=ax, palette='Set2')
sns.swarmplot(x='QUARTER', y='underemp_rate', data=quarterly_df, color=".25", size=6, alpha=0.7)

ax.set_title('Distribution of Underemployment by Quarter (Seasonality Check)', fontsize=14, fontweight='bold')
ax.set_xlabel('Quarter', fontweight='bold')
ax.set_ylabel('Underemployment Rate (%)', fontweight='bold')
ax.set_xticklabels(['Q1', 'Q2', 'Q3', 'Q4'])

plt.tight_layout()
plt.savefig('Visualizations/Quarterly_Seasonality_Boxplots.png', dpi=300, bbox_inches='tight')
plt.close()

# ---------------------------------------------------------
# 3. Economic Regime Comparison (Violin / KDE Plots)
# ---------------------------------------------------------
print("Generating Economic Regime Comparison...")
# Define Regimes: Pre-COVID (2015-2019) vs Crisis Era (2020-2024)
quarterly_df['Regime'] = np.where(quarterly_df['YEAR'] < 2020, 'Normal Economy (2015-2019)', 'Crisis & Recovery (2020-2024)')

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Violin Plot
sns.violinplot(x='Regime', y='underemp_rate', data=quarterly_df, ax=axes[0], palette=[COLOR_NORMAL, COLOR_CRISIS], inner='quartile')
axes[0].set_title('Underemployment Rate Spread by Economic Regime', fontweight='bold')
axes[0].set_ylabel('Underemployment Rate (%)')
axes[0].set_xlabel('')

# KDE Plot
sns.kdeplot(data=quarterly_df[quarterly_df['Regime'] == 'Normal Economy (2015-2019)']['underemp_rate'], ax=axes[1], color=COLOR_NORMAL, fill=True, label='Normal Economy')
sns.kdeplot(data=quarterly_df[quarterly_df['Regime'] == 'Crisis & Recovery (2020-2024)']['underemp_rate'], ax=axes[1], color=COLOR_CRISIS, fill=True, label='Crisis Era')
axes[1].set_title('Probability Density of Underemployment', fontweight='bold')
axes[1].set_xlabel('Underemployment Rate (%)')
axes[1].legend()

plt.tight_layout()
plt.savefig('Visualizations/Regime_Comparison_Violin_KDE.png', dpi=300, bbox_inches='tight')
plt.close()

# ---------------------------------------------------------
# 4. Lagged Cross-Correlation (TLCC)
# ---------------------------------------------------------
print("Generating Time Lagged Cross-Correlation...")

# We will use master_df (yearly) as an example to show lag effects of Real GDP on Underemployment
lags = range(0, 4) # 0 to 3 years lag
corrs = []

# Ensure data is sorted by year
master_sorted = master_df.sort_values('Year').copy()

for lag in lags:
    # Shift Real GDP forward by 'lag' years to see its effect on FUTURE underemployment
    shifted_gdp = master_sorted['Real_GDP'].shift(lag)
    # the dropna is needed to align the series sizes for correlation
    valid_idx = shifted_gdp.notna() & master_sorted['Underemployment_Rate'].notna()
    corr = master_sorted.loc[valid_idx, 'Underemployment_Rate'].corr(shifted_gdp.loc[valid_idx], method='pearson')
    corrs.append(corr)

fig, ax = plt.subplots(figsize=(8, 5))
markerline, stemlines, baseline = ax.stem(lags, corrs, basefmt="k--")
plt.setp(markerline, marker='o', markersize=8, color='purple')
plt.setp(stemlines, color='purple', linewidth=2)

ax.set_title('Time-Lagged Cross-Correlation:\nReal GDP vs Underemployment (0 to 3 Years Lag)', fontsize=12, fontweight='bold')
ax.set_xlabel('Lag (Years)', fontweight='bold')
ax.set_ylabel('Pearson Correlation Coefficient', fontweight='bold')
ax.set_xticks(lags)
ax.set_ylim(-1.0, 1.0)
ax.grid(True, linestyle='--', alpha=0.5)

# Add annotations
for i, txt in enumerate(corrs):
    ax.annotate(f'{txt:.2f}', (lags[i], corrs[i]), textcoords="offset points", xytext=(0,10), ha='center')

plt.tight_layout()
plt.savefig('Visualizations/Lagged_Correlation_TLCC.png', dpi=300, bbox_inches='tight')
plt.close()

print("All advanced visualizations generated successfully!")
