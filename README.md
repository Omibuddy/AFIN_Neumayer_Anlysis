# Polar sea-ice timing (Arctic + Antarctic)

**Has polar sea-ice timing shifted?** We analyze:

- **Arctic**: day-of-year (DOY) of the **hemispheric sea-ice area (SIA) annual minimum** (OSI SAF)
- **Antarctic (Atka Bay / Neumayer Station III)**: DOY of the **last AFIN fast-ice survey** as a **breakup proxy**

Observational climate analysis for University of Hamburg (M.Sc. Data Science & AI), reference period **April 2026**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Key results (April 2026 analysis)

| Metric | Value |
|--------|-------|
| Arctic period | **1979–2025** (last complete minimum before Apr 2026) |
| Antarctic period | **2010–2018** (AFIN/PANGAEA availability used here) |
| Data cutoff | **2026-04-30** |
| Arctic OLS trend | **−0.08 days/year** (*p* = 0.65; not significant) |
| Antarctic OLS trend | **+29.45 days/year** (*p* = 0.21; not significant; strong interannual variability) |
| Conclusion | No statistically significant shift in **timing** through April 2026 in either series |

![Polar comparison figure](results/figures/polar_ice_timing_comparison.png)

> Full numbers: [`results/summary.json`](results/summary.json) · Auto-generated write-up: [`docs/RESULTS.md`](docs/RESULTS.md)

## Quick start

```bash
# 1. Clone and enter project
cd arctic-sia-minimum-timing   # your repo name

# 2. Virtual environment (recommended on Mac M2)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Download data (small; includes AFIN via PANGAEA)
python scripts/download_data.py

# 4. Run analysis + refresh docs + LaTeX source
python scripts/run_analysis.py

# 5. Optional: compile one-page PDF (requires TeX Live / MacTeX)
make pdf
# Output: report/one_pager.pdf
```

Or use Make:

```bash
make setup    # create venv + install deps
make data     # download official datasets
make analyze  # run pipeline
make pdf      # compile LaTeX report
```

## Project structure

```
├── README.md                 # This file
├── config.yaml               # Analysis settings (April 2026 cutoff)
├── requirements.txt
├── Makefile
├── scripts/
│   ├── download_data.py      # Fetch OSI SAF, NSIDC, AFIN (PANGAEA)
│   ├── run_analysis.py       # Main pipeline
│   ├── update_docs.py        # Regenerate docs/RESULTS.md
│   └── generate_latex.py     # Regenerate report/one_pager.tex
├── src/                      # Loaders, statistics, plotting
├── data/raw/                 # Official inputs (small)
├── results/
│   ├── summary.json          # Machine-readable results
│   ├── figures/              # Main plot
│   └── tables/               # Annual minimum CSVs
├── docs/                     # Detailed documentation
├── report/
│   └── one_pager.tex         # One-page report (course template)
└── readme                    # Original assignment brief
```

## Documentation

| Document | Description |
|----------|-------------|
| [docs/DATA.md](docs/DATA.md) | Data sources (OSI SAF, NSIDC, AFIN/PANGAEA) |
| [docs/METHODS.md](docs/METHODS.md) | Statistical methods and design choices |
| [docs/RESULTS.md](docs/RESULTS.md) | **Auto-generated** results after each run |
| [docs/GITHUB.md](docs/GITHUB.md) | Publishing and updating on GitHub |
| [docs/ML_NOTES.md](docs/ML_NOTES.md) | Why classical stats, not deep learning |

## One-page report

Edit your name in `config.yaml` → `project.author`, then:

```bash
python scripts/run_analysis.py   # refreshes report/one_pager.tex
cd report && pdflatex one_pager.tex && pdflatex one_pager.tex
```

## Updating for new data

When OSI SAF / NSIDC release new months:

1. `python scripts/download_data.py`
2. Adjust `dates.data_cutoff` in `config.yaml` if needed
3. `python scripts/run_analysis.py`

`docs/RESULTS.md` and `report/one_pager.tex` update automatically.

## Citation

**Data**

- Thomae, S., et al. (2025). UHH sea-ice area product. doi:[10.25592/uhhfdm.18163](https://doi.org/10.25592/uhhfdm.18163)
- EUMETSAT OSI SAF Sea Ice Index v3.0. doi:[10.15770/EUM_SAF_OSI_0023](https://doi.org/10.15770/EUM_SAF_OSI_0023)
- NSIDC Sea Ice Index G02135 v4.0. [https://nsidc.org/data/g02135](https://nsidc.org/data/g02135)

**Reference**

- Notz, D., & Stroeve, J. (2016). Observed Arctic sea-ice loss directly follows anthropogenic CO₂ emission. *Science*, 354(6313), 747–750.

## License

Code: MIT ([LICENSE](LICENSE)). Third-party data remain under their respective licenses (CC-BY / open access).
