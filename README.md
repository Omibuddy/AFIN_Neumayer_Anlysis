# Polar sea-ice timing (Arctic + Antarctic)

**Has polar sea-ice timing shifted — and if not, why is it noisy?**

University of Hamburg · M.Sc. Data Science & AI · 6-credit sea ice course (June/July 2026)  
**Author:** Omkar Kondhalkar · **Data cutoff:** 2026-04-30

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Headline

**Magnitude loss ≠ calendar shift.**

| Phase | Question | Result |
|-------|----------|--------|
| **Phase 1** | Has minimum *timing* shifted? | Arctic −0.08 d yr⁻¹ (*p* = 0.65); Antarctic AFIN +29.45 d yr⁻¹ (*p* = 0.21) — both **not significant** |
| **Phase 2** | Does pre-melt (July) SIC *spatially* predict early vs. late minima? | **0 / 15,883** ocean pixels survive FDR correction; Beaufort/Kara/MIZ region tests non-significant |

Phase 2 does not replace Phase 1 — it tests whether spatial ice structure explains the interannual variability the scalar trend leaves unexplained. It does not, once multiple comparisons are handled honestly.

---

## Phase 1 — Classical timing trends

**Arctic:** OSI SAF daily hemispheric SIA; annual minimum DOY (July–December), 1979–2025.  
**Antarctic:** AFIN manual transect surveys at Atka Bay (Neumayer III), 2010–2018 (*n* = 9); breakup proxy = last survey date per season.

![Phase 1: Arctic minimum DOY (left) and Antarctic AFIN breakup proxy (right)](results/figures/polar_ice_timing_comparison.png)

> Machine-readable output: [`results/summary.json`](results/summary.json)

---

## Phase 2 — Sensitivity + spatial null test

### Fig 2 — Amount vs. timing (decoupled)

SIA at minimum declines; minimum *date* does not show a robust trend.

![Arctic SIA at minimum vs minimum DOY dual-axis](results/figures/arctic_sia_minimum_vs_doy_dual_axis.png)

### Fig 3 — Aug 31 SIA vs. minimum DOY (scalar baseline)

![Aug 31 hemispheric SIA vs annual minimum DOY](results/figures/arctic_aug31_sia_vs_min_doy.png)

### Fig 5 — Spatial Pearson-r + tercile composite (core Phase 2)

NSIDC CDRv6 G02202 July SIC (25 km polar stereographic, 60–90°N, 160×160). Years ranked into early/late terciles by minimum DOY (*n* = 15 each). Pixel-wise Pearson *r* between July SIC and minimum DOY, plus early−late composite. **Benjamini–Hochberg FDR correction (q = 0.05): 0 significant pixels.**

![Spatial structure of Arctic minimum-DOY variability](results/figures/fig5_spatial_heatmap.png)

| Region (region-mean test) | *r* | *p* |
|---------------------------|-----|-----|
| Beaufort | 0.01 | 0.96 |
| Kara | −0.11 | 0.45 |
| MIZ | −0.13 | 0.39 |

> Spatial tables: [`results/tables/spatial/`](results/tables/spatial/)

### Fig 4 — Antarctic AFIN calendar + WMO context

![Antarctic AFIN survey calendar, Atka Bay 2010–2018](results/figures/antarctic_afin_calendar.png)

---

## Conclusion (three levels)

1. **Scalar trends:** No statistically significant shift in Arctic or Antarctic minimum timing.
2. **Spatial test:** Static July SIC does not predict which years have early vs. late minima (null after FDR correction).
3. **Mechanistic context:** Literature attributes Beaufort/Kara timing variability to *within-season* synoptic wind forcing (Nie et al. 2025; Yang et al. 2024), not antecedent ice state — a concrete direction for future work (e.g. ERA5 wind correlations).

---

## Reports & slides

| Document | Source | Compile |
|----------|--------|---------|
| **One-pager** (Phase 1 submission) | `report/one_pager.tex` | `make pdf` |
| **Full report** (Phase 1 + 2) | `report/full_report.tex` | `make report` → `report/full_report.pdf` |
| **Slides** (~10 min) | `report/slides.tex` | `make report` → `report/slides.pdf` |

See [`report/README.md`](report/README.md) for LaTeX details.

---

## Quick start

```bash
git clone https://github.com/Omibuddy/AFIN_Neumayer_Anlysis.git
cd AFIN_Neumayer_Anlysis

# Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Phase 1 data + analysis
python scripts/download_data.py
python scripts/run_analysis.py

# Phase 2 (downloads CDRv6 grids, sensitivity, spatial, Antarctic figures)
make phase2

# Compile all PDFs (requires TeX Live / MacTeX)
make pdf      # one_pager.pdf
make report   # full_report.pdf + slides.pdf
```

Or with Make:

```bash
make setup
make data
make analyze    # Phase 1
make phase2     # Phase 2
make report     # full report + slides
```

**Note:** NSIDC CDRv6 gridded files (~57 MB) are downloaded by `scripts/download_gridded.py` and gitignored. Re-run `make phase2` on a fresh clone.

---

## Project structure

```
├── README.md
├── config.yaml
├── requirements.txt
├── Makefile
├── scripts/
│   ├── download_data.py          # OSI SAF, NSIDC extent, AFIN (PANGAEA)
│   ├── download_gridded.py       # NSIDC CDRv6 monthly SIC (Phase 2)
│   ├── run_analysis.py           # Phase 1 pipeline
│   ├── run_phase2.py             # Phase 2 orchestrator
│   ├── sensitivity_analysis.py   # Figs 2 + 3
│   ├── spatial_exploration.py    # Fig 5 (Pearson-r + composite + FDR)
│   └── plot_antarctic_calendar.py # Fig 4
├── src/
│   ├── load_data.py
│   ├── load_afin.py
│   ├── gridded_sic.py            # CDRv6 grid loader
│   ├── statistics.py
│   └── plotting.py
├── data/raw/                     # Small official inputs (CDRv6 excluded)
├── results/
│   ├── summary.json
│   ├── figures/                  # All PNG outputs
│   └── tables/
│       ├── arctic_annual_minimum_doy_osisaf_sia.csv
│       └── spatial/              # r_map, p_map, region tests
├── docs/
└── report/
    ├── one_pager.tex             # Phase 1 (auto-generated)
    ├── full_report.tex           # Phase 1 + 2 write-up
    └── slides.tex                # Presentation (~7 slides)
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [report/README.md](report/README.md) | LaTeX: one-pager, full report, slides |
| [docs/DATA.md](docs/DATA.md) | Data sources (OSI SAF, NSIDC, AFIN/PANGAEA, CDRv6) |
| [docs/METHODS.md](docs/METHODS.md) | Statistical methods and design choices |
| [docs/RESULTS.md](docs/RESULTS.md) | Auto-generated Phase 1 results |
| [docs/ML_NOTES.md](docs/ML_NOTES.md) | Why classical stats over deep learning |
| [docs/GITHUB.md](docs/GITHUB.md) | Publishing on GitHub |

---

## Citation

**Data**

- EUMETSAT OSI SAF Sea Ice Index v3.0. doi:[10.15770/EUM_SAF_OSI_0023](https://doi.org/10.15770/EUM_SAF_OSI_0023)
- NSIDC Sea Ice Index G02135 v4.0 · NSIDC CDRv6 G02202
- PANGAEA AFIN Atka Bay surveys · Arndt et al. (2020), *The Cryosphere*

**Key references (Phase 2 discussion)**

- Nie, Zheng, Wei, Zhao & Luo (2025). Beaufort Sea ice retreat mechanisms. *Remote Sensing*, 17(19), 3286.
- Yang, Nie, Zhang, Luo, Wei & Zhao (2024). Kara Sea open-water onset variability. *J. Climate*, 37(4), 1367–1381.
- Wang, Lohmann, Gou et al. (2026). Arctic MIZ SIC variability. *Geophys. Res. Lett.*, 53(7). doi:[10.1029/2025GL119415](https://doi.org/10.1029/2025GL119415)
- WMO (2026). *State of the Global Climate 2025*.

## License

Code: MIT ([LICENSE](LICENSE)). Third-party data remain under their respective licenses.
