# Machine learning vs classical statistics

This note explains technology choices for an **M.Sc. Data Science & AI** project that is intentionally **not** a deep-learning exercise.

## Assignment fit

The course question is:

> Has the day-of-year of the Arctic SIA annual minimum shifted over the satellite era?

After aggregation you have **one number per year** (~47 points). The required output is:

- One trend plot with confidence interval
- Linear trend + significance test
- One-page written report

That is **observational climatology**, not computer vision.

## What recent ML sea-ice work actually does

| Model family | Typical task | Data |
|--------------|--------------|------|
| U-Net / IceNet | Seasonal **SIC maps** | Gridded satellite + reanalysis |
| Transformer (SICNetseason) | 6-month **SIC** forecast | Decades of 2D fields |
| State-space (IceMamba) | Pan-Arctic **concentration** | High-dimensional spatiotemporal |

References: [SICNetseason (GMD 2025)](https://gmd.copernicus.org/articles/18/2665/2025/), [MT-IceNet (arXiv)](https://arxiv.org/pdf/2308.04511), [IceMamba (Nature 2025)](https://www.nature.com/articles/s41612-025-01058-0).

These are valuable for **spatial prediction** but inappropriate here:

- n ≈ 47 at the annual level → severe overfitting risk for neural nets
- No spatial structure left after hemispheric integration
- Reviewers expect transparent trend statistics in climate indicators

## Methods we use (and why they are “high standard”)

| Method | Role |
|--------|------|
| OLS + *p*-value | Direct answer to “shifted?” |
| Bootstrap CI | Non-Gaussian, small-sample uncertainty |
| Theil–Sen | Robust to outlier years |
| Multi-product check | OSI SIA + NSIDC extent → scientific rigor |

## Optional ML-adjacent extensions (if course allows extra credit)

1. **Changepoint detection** (`ruptures`, PELT) — step change vs gradual trend  
2. **Gaussian process** on DOY — flexible trend with uncertainty bands  
3. **Cross-validation across products** — Walsh/OSI/NASA-Team from UHH monthly NetCDF  

None of these replace the core OLS + plot required by the brief.

## Mac M2 constraints

| Approach | RAM | Storage | Fits M2? |
|----------|-----|---------|----------|
| This project (CSV + pandas) | < 500 MB | ~3 MB data | Yes |
| Gridded CDR + PyTorch U-Net | 8+ GB | 50+ GB | No |

## Bottom line

Using **classical, reproducible statistics** on **official index time series** is the correct match for the question — not a limitation of the project.
