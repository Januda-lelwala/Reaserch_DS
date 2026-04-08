# Data Imputation Audit Report

This audit details the computationally generated fills for missing data within the master dataset.
Notice: MICE was generated across $m=5$ datasets. Point estimate values below reflect **Seed 0** for illustrational purposes. Proper standard errors should pool across all 5 exported databases.

| Variable | Year | Method | Reason | Seed 0 Imputed Value | Plausible Bounds | Used In |
|----------|------|--------|--------|----------------------|------------------|---------|
| `Real_GDP` | **2024** | KNN | *isolated gap* | 300583.6629 | ~292653.41 | Both (Annual & Quarterly) |
| `GDP_Growth_Rate` | **2024** | KNN | *isolated gap* | 0.6269 | ~-2.30 | Both (Annual & Quarterly) |
