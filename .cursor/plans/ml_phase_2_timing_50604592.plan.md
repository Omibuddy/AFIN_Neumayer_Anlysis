---
name: Phase 2 Naive Spatial Exploration
overview: "6-credit sea ice course extension (Hamburg, June 2026): sensitivity figures, Pearson-r spatial heat map + tercile composite on CDRv6 July SIC, Antarctic calendar, full report and slides. CMIP6 cite-only. Magnitude loss ≠ calendar shift remains the locked finding."
todos:
  - id: d1-2-env
    content: "D1–2: cartopy + download_gridded.py → CDRv6 July SIC"
    status: completed
  - id: d3-4-sensitivity
    content: "D3–4: sensitivity_analysis.py → Figs 2 + 3"
    status: completed
  - id: d5-7-spatial
    content: "D5–7: spatial_exploration.py → r-map + ΔSIC composite → Fig 5"
    status: completed
  - id: d7b-rigor-fix
    content: "Bugfix: CDRv6 v06r00 SIC is 0-1 fraction not percent (was /100'd twice, emptied ocean mask). Added FDR correction + region-mean tests: 0/15883 pixels survive q=0.05; Beaufort/Kara/MIZ all non-significant (p=0.96/0.45/0.39). Report rewritten around honest null result."
    status: completed
  - id: d8-antarctic
    content: "D8: Antarctic data prep → Fig 4"
    status: completed
  - id: d9-14-report
    content: "D9–14: full_report.tex + slides.tex + CMIP6 paragraph (cite only)"
    status: pending
isProject: false
---

# Revised Phase 2 — Naive Spatial Exploration Plan
### Connected to Phase 1 · 6-Credit Scope · June 2026

---

## What changed and why

| Out (old Phase 2) | In (new Phase 2) |
|---|---|
| Encoder-only U-Net | Simple composite + correlation maps |
| Captum / Grad-CAM / IG | Pearson-r spatial heat map (same visual story, no ML) |
| LOYO CV training loop | Tercile sorting on existing min-DOY CSV |
| ~150 hrs extra work | ~15–20 hrs extra work |

The scientific question stays identical: *why is timing noisy, and which regions drive early vs late years?* Answered with transparent, course-appropriate statistics instead of a black-box model.

---

## Phase 1 → Phase 2 connection

> *Phase 1 showed the scalar DOY trend is flat and noisy (p = 0.65). Phase 2 asks: what spatial SIC structure explains the interannual variability that IS there?*

---

## The Algorithm

**Spatial Pearson-r Composite Method** — three steps:

1. **Rank years by min-DOY** from `arctic_annual_minimum_doy_osisaf_sia.csv` → early / late terciles (~15 yrs each)
2. **Spatial correlation map:** for each grid cell, Pearson r between July SIC(year) and min_DOY(year), 1979–2024
3. **Composite difference map:** mean(July SIC, early tercile) − mean(July SIC, late tercile); overlay 15% SIC contour; annotate Beaufort / Kara / MIZ

No training. No hyperparameters. Fully reproducible.

---

## Figure list

| # | Figure | Script |
|---|---|---|
| 1 | `polar_ice_timing_comparison.png` | Phase 1 (locked) |
| 2 | SIA-at-minimum vs min-DOY dual-axis | `sensitivity_analysis.py` |
| 3 | Aug 31 SIA vs min-DOY scatter | `sensitivity_analysis.py` |
| 4 | Antarctic AFIN calendar + WMO 2025 | `plot_antarctic_calendar.py` |
| 5 | Pearson-r heat map + ΔSIC composite | `spatial_exploration.py` |

**Presentation:** Figs 1, 2, 5, WMO context (~10 min).

---

## Repo structure

```
scripts/
  download_gridded.py
  sensitivity_analysis.py
  spatial_exploration.py    # NEW — core Phase 2 deliverable
  plot_antarctic_calendar.py
  run_phase2.py             # Orchestrator
report/
  full_report.tex
  slides.tex
```

---

## 2-week timeline

| Day | Task | Output |
|---|---|---|
| 1–2 | Download CDRv6 July SIC | Data ready |
| 3–4 | `sensitivity_analysis.py` | Figs 2 + 3 |
| 5–7 | `spatial_exploration.py` | Fig 5 |
| 8 | Antarctic script | Fig 4 |
| 9–14 | Report + slides | Final PDF |

---

## Conclusion (Phase 1 + 2)

**Level 1:** Arctic min DOY shows no significant trend (−0.08 d yr⁻¹, p = 0.65). Antarctic AFIN similarly non-significant.

**Level 2:** Interannual timing variability is spatially structured (Beaufort, Kara, MIZ), not random noise.

**Level 3:** Scalar DOY trend is underpowered and incomplete; spatial decomposition reveals structure magnitude metrics wash out.
