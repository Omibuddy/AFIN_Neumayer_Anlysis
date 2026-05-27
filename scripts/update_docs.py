#!/usr/bin/env python3
"""Regenerate docs/RESULTS.md from results/summary.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _stats_table(t: dict, label: str) -> str:
    sig = "Yes" if t["significant_at_0_05"] else "No"
    mk = t.get("mann_kendall_p")
    mk_row = f"| Mann–Kendall *p* | {mk:.4f} |\n" if mk is not None else ""
    return f"""### {label}

| Statistic | Value |
|-----------|-------|
| Period | {t['year_start']}–{t['year_end']} (*n* = {t['n_years']}) |
| Mean DOY | {t['mean_doy']:.1f} (σ = {t['std_doy']:.1f}) |
| OLS slope | {t['slope_days_per_year']:+.3f} days yr⁻¹ ({t['slope_days_per_decade']:+.1f} days decade⁻¹) |
| 95% bootstrap CI | [{t['ci_lower']:.3f}, {t['ci_upper']:.3f}] days yr⁻¹ |
| *p*-value | {t['p_value']:.4f} |
| Significant (α = 0.05)? | {sig} |
| Direction | {t['interpretation_direction']} |
{mk_row}"""


def main() -> None:
    with (ROOT / "results" / "summary.json").open() as f:
        s = json.load(f)

    ar = s["arctic"]["trend"]
    ant = s["antarctic"]["trend"]
    ext = s["arctic"]["nsidc_extent_sensitivity"]

    md = f"""# Results (auto-generated)

> **{s['analysis_reference']}** | Data cutoff: **{s['data_cutoff']}**

## Combined finding

Neither **Arctic** pan-hemispheric minimum timing nor **Antarctic** Atka Bay fast-ice breakup timing shows a **statistically significant** linear trend at the 5% level through April 2026. Ice **amount** continues to decline in the Arctic; local fast ice in Atka Bay shows strong **interannual variability** (AFIN / Neumayer III).

![Polar comparison](../results/figures/polar_ice_timing_comparison.png)

---

## Arctic — sea-ice area annual minimum (OSI SAF)

{_stats_table(ar, "Arctic SIA minimum DOY")}

**Interpretation:** September minimum **extent/area** has fallen sharply since 1979, but the calendar date of the minimum remains variable (early–late September). No robust shift in timing (*p* = {ar['p_value']:.3f}).

NSIDC extent sensitivity: slope {ext['slope_days_per_year']:+.3f} days yr⁻¹, *p* = {ext['p_value']:.4f}.

![Arctic](../results/figures/arctic_sia_minimum_doy_trend.png)

---

## Antarctic — fast-ice breakup proxy (AFIN / Neumayer III / Atka Bay)

**Method:** Last in situ AFIN transect survey date each austral season (2010–2018, PANGAEA).  
**Context:** Neumayer Station III overwintering team; **SPOT** penguin observatory monitors emperor penguins on adjacent fast ice.

{_stats_table(ant, "Last AFIN survey DOY (breakup proxy)")}

**Interpretation:** Breakup/survey-end dates range from late austral spring to mid-summer (DOY ~160–380). Arndt et al. (2020) report strong interannual variability (e.g. iceberg blocking in 2013, 2016) without a multi-year thickness trend over 2010–2018. Our timing trend over the same period is also **not significant** (*p* = {ant['p_value']:.3f}).

![Antarctic](../results/figures/antarctic_fast_ice_breakup_doy_trend.png)

---

## Data tables

| File | Content |
|------|---------|
| `results/tables/arctic_annual_minimum_doy_osisaf_sia.csv` | Arctic minimum DOY |
| `results/tables/antarctic_annual_breakup_doy_afin.csv` | Antarctic breakup proxy |
| `results/tables/antarctic_afin_all_surveys.csv` | All AFIN survey records |

## Reproduce

```bash
python scripts/download_data.py
python scripts/run_analysis.py
```
"""

    out = ROOT / "docs" / "RESULTS.md"
    out.write_text(md)
    print(f"Updated {out}")


if __name__ == "__main__":
    main()
