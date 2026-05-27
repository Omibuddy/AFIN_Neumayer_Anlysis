# Data sources

All inputs are **official**, publicly available products. Total download size is about **3 MB** — suitable for a MacBook Air M2 without external storage.

**Analysis reference:** April 2026 (`data_cutoff: 2026-04-30` in `config.yaml`).

## Primary: daily Arctic sea-ice area (SIA)

| Field | Value |
|-------|-------|
| Product | EUMETSAT OSI SAF Sea Ice Index v3.0 |
| Variable | Northern Hemisphere daily **sea-ice area** |
| File | `data/raw/osisaf/ice_area_nh_sii-v3p0_daily.txt` |
| URL | `ftp://osisaf.met.no/prod/ice/index/v3p0/timeseries/nh/ice_area_nh_sii-v3p0_daily.txt` |
| DOI | [10.15770/EUM_SAF_OSI_0023](https://doi.org/10.15770/EUM_SAF_OSI_0023) |
| Portal | [OSI SAF Sea Ice Index](https://osisaf-hl.met.no/v3p0-sea-ice-index) |

**Why this product?** The UHH Sea-Ice Area product (Notz/Kern group) is published as **monthly** aggregates but is computed from the same OSI SAF daily concentration lineage. For **day-of-year of the annual minimum**, daily SIA is required; OSI SAF index files are the lightweight, consistent choice.

**SIA definition (OSI SAF):** Sum of grid-cell areas with concentration > 0%, weighted by concentration (area-fraction integral).

## Sensitivity: daily Arctic sea-ice extent (SIE)

| Field | Value |
|-------|-------|
| Product | NSIDC Sea Ice Index v4.0 (G02135) |
| Variable | Northern Hemisphere daily **extent** |
| File | `data/raw/nsidc/N_seaice_extent_daily_v4.0.csv` |
| URL | [NOAA@NSIDC HTTPS](https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v4.0.csv) |
| DOI | [10.7265/N5K072F8](https://doi.org/10.7265/N5K072F8) |

**Extent vs area:** Extent counts grid cells with ≥ 15% ice; area weights by concentration. Minimum **timing** is usually similar but not identical.

## Antarctic: AFIN fast-ice surveys (Atka Bay / Neumayer III)

These are **manual in situ** measurements from the **Antarctic Fast Ice Network (AFIN)** at Atka Bay (near Neumayer Station III), published on **PANGAEA**.

| Field | Value |
|-------|-------|
| Network | AFIN |
| Station / site | Neumayer III / Atka Bay |
| Years used here | 2010–2018 (PANGAEA DOIs; see `config.yaml`) |
| Format | Tab-separated text via DOI (content negotiation) |
| Bibliography DOI | [10.1594/PANGAEA.908860](https://doi.org/10.1594/PANGAEA.908860) |
| Access method | `curl -H 'Accept: text/tab-separated-values' https://doi.pangaea.de/10.1594/PANGAEA.xxxxxx` |

**Breakup proxy used:** the **last survey date** in each season (AFIN teams typically stop when ice becomes unsafe/ice-free).

## April 2026 handling

| Rule | Implementation |
|------|----------------|
| Daily data used | Only dates ≤ **2026-04-30** |
| Last minimum year | **2025** (2026 melt season not complete in April) |
| Satellite era | **1979–2025** (excludes partial 1978 melt season) |
| Antarctic AFIN period | **2010–2018** (public PANGAEA AFIN series used here) |

## Download

```bash
python scripts/download_data.py
```

## What we deliberately do **not** download

| Product | Typical size | Reason |
|---------|--------------|--------|
| OSI-450 gridded daily NetCDF | 10+ GB | Unnecessary for hemispheric SIA time series |
| NSIDC passive microwave CDR G02202 | 10+ GB | Index files already provide daily extent |

## Processed outputs (generated)

- `results/tables/arctic_annual_minimum_doy_osisaf_sia.csv`
- `results/tables/arctic_annual_minimum_doy_nsidc_extent.csv`
- `results/tables/antarctic_annual_breakup_doy_afin.csv`
- `results/tables/antarctic_afin_all_surveys.csv`
- `results/summary.json`
