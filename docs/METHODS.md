# Methods

## Research question

This project answers two timing questions (April 2026 reference):

1. **Arctic (pan-hemispheric):** Has the day-of-year of the **sea-ice area (SIA)** annual minimum shifted earlier or later during the satellite era?
2. **Antarctic (local fast ice):** Has the day-of-year of **Atka Bay landfast-ice breakup** shifted (proxied by the last AFIN in situ survey date each season)?

## Procedure

### Arctic

1. **Load** daily Northern Hemisphere SIA from OSI SAF (see [DATA.md](DATA.md)).
2. **Filter** observations to dates on or before **2026-04-30**.
3. **For each year** from 1979 to 2025 (last complete melt minimum before April 2026):
   - Restrict to **July–December**.
   - Find the date with **minimum SIA**.
   - Record **DOY** of that date.
4. **Fit** OLS trend: `minimum_doy ~ year` + 95% bootstrap CI; Theil–Sen check.
5. **Sensitivity:** repeat with NSIDC daily **extent**.

### Antarctic (AFIN / Neumayer III / Atka Bay)

1. **Download** annual AFIN survey tables for **2010–2018** from PANGAEA (DOIs in `config.yaml`).
2. For each year, compute a **breakup timing proxy** as the **maximum survey date** in that season.
3. Convert that date to **DOY** and fit the same trend statistics (OLS + bootstrap CI + Theil–Sen).

## Why this approach is appropriate

| Criterion | Assessment |
|-----------|------------|
| Question type | Single scalar climate indicator per year → time-series trend |
| Sample size | n ≈ 47 annual values → classical inference, not deep learning |
| Physical interpretability | Slope in **days per year** is directly readable |
| Community practice | Standard for sea-ice climate indicators (NSIDC, OSI SAF, IPCC-style assessments) |

Deep learning (CNN, Transformer, LSTM on grids) targets **spatial forecasting** of concentration fields. With ~47 years of aggregated data, neural networks would **overfit** and obscure the transparent answer the assignment requires.
For the Antarctic component, sample size is even smaller (*n* = 9 years), reinforcing the need for transparent, robust statistics rather than ML.

## Statistical details

### OLS linear trend

\[
\text{DOY}_t = \beta_0 + \beta_1 \cdot \text{Year}_t + \varepsilon_t
\]

We report \(\beta_1\) in days/year and days/decade, Pearson \(r\), and two-sided \(p\)-value.

### Bootstrap

Residual pairs \((\text{Year}, \text{DOY})\) are resampled with replacement 5000 times. The 2.5% and 97.5% quantiles of \(\beta_1\) form the 95% CI on the slope.

### Theil–Sen

Median-based slope; robust to outliers (e.g. anomalous storm years shifting the minimum by a week).

### Significance

Null hypothesis: no linear trend (\(\beta_1 = 0\)). We use \(\alpha = 0.05\).

Optional: install `pymannkendall` for Mann–Kendall test (non-parametric monotonic trend).

## Uncertainties and limitations

1. **Weather variability** dominates interannual minimum **date** more than long-term forcing.
2. **Extent vs area:** Primary analysis uses SIA; NSIDC extent sensitivity may differ slightly.
3. **Early record:** SMMR period (1978–1987) had every-second-day sampling; OSI/NSIDC apply gap handling.
4. **Melt window:** July–December is inclusive; sensitivity to Aug–Oct-only window is possible (document if tested).
5. **April 2026 cutoff:** 2026 is excluded from annual minima because the summer 2026 minimum has not occurred yet.
6. **AFIN breakup proxy:** using the last survey date depends on logistics and safety constraints. It is a defensible proxy for “end of accessible fast ice”, but not a perfect physical breakup timestamp.

## Reproducibility

```bash
python scripts/run_analysis.py
```

Configuration: `config.yaml`
