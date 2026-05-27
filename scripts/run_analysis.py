#!/usr/bin/env python3
"""
Polar sea-ice timing analysis — Arctic + Antarctic (April 2026 reference).

Arctic: day-of-year of hemispheric SIA annual minimum (OSI SAF).
Antarctic: day-of-year of last AFIN fast-ice survey in Atka Bay (Neumayer III).
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.load_afin import load_all_afin_years
from src.load_data import (
    annual_minimum_doy,
    last_complete_minimum_year,
    load_nsidc_daily_extent,
    load_osisaf_daily_sia,
)
from src.plotting import plot_doy_trend, plot_polar_comparison
from src.statistics import compute_trend, mann_kendall_pvalue


def _direction(slope: float) -> str:
    if slope < 0:
        return "earlier"
    if slope > 0:
        return "later"
    return "unchanged"


def _trend_block(trend, mk_p, alpha: float) -> dict:
    return {
        **{k: v for k, v in asdict(trend).items()},
        "slope_days_per_decade": trend.slope_days_per_year * 10,
        "mann_kendall_p": mk_p,
        "significant_at_0_05": trend.p_value < alpha,
        "interpretation_direction": _direction(trend.slope_days_per_year),
    }


def main() -> None:
    with (ROOT / "config.yaml").open() as f:
        cfg = yaml.safe_load(f)

    cutoff = pd.Timestamp(cfg["dates"]["data_cutoff"])
    melt_start = int(cfg["dates"]["arctic_melt_month_start"])
    melt_end = int(cfg["dates"]["arctic_melt_month_end"])
    arctic_start = int(cfg["dates"]["arctic_era_start"])
    last_arctic_year = last_complete_minimum_year(cutoff, melt_end)

    results_dir = ROOT / cfg["paths"]["results_dir"]
    figures_dir = ROOT / cfg["paths"]["figures_dir"]
    tables_dir = ROOT / cfg["paths"]["tables_dir"]
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    boot_n = cfg["analysis"]["bootstrap_iterations"]
    boot_conf = cfg["analysis"]["confidence_level"]
    boot_seed = cfg["analysis"]["bootstrap_seed"]
    alpha = cfg["analysis"]["significance_alpha"]
    dpi = int(cfg["plot"]["dpi"])

    # ── Arctic ──────────────────────────────────────────────────────────────
    daily_sia = load_osisaf_daily_sia(ROOT / cfg["paths"]["osisaf_daily_sia"], cutoff)
    annual_arctic = annual_minimum_doy(
        daily_sia, "sia_mkm2", melt_start, melt_end, last_arctic_year
    )
    annual_arctic = annual_arctic[annual_arctic["year"] >= arctic_start].reset_index(drop=True)
    trend_arctic = compute_trend(annual_arctic, boot_n, boot_conf, boot_seed)
    mk_arctic = mann_kendall_pvalue(annual_arctic["minimum_doy"].to_numpy())

    daily_ext = load_nsidc_daily_extent(ROOT / cfg["paths"]["nsidc_daily_extent"], cutoff)
    annual_ext = annual_minimum_doy(
        daily_ext, "extent_mkm2", melt_start, melt_end, last_arctic_year
    )
    annual_ext = annual_ext[annual_ext["year"] >= arctic_start].reset_index(drop=True)
    trend_ext = compute_trend(annual_ext, boot_n, boot_conf, boot_seed)

    # ── Antarctic (AFIN / Neumayer III, Atka Bay) ─────────────────────────
    ant_cfg = cfg["antarctic"]
    dois = {int(k): v for k, v in ant_cfg["pangaea_dois"].items()}
    surveys, annual_antarctic = load_all_afin_years(
        ROOT / cfg["paths"]["afin_dir"], dois, download_missing=True
    )
    era_a0, era_a1 = int(ant_cfg["era_start"]), int(ant_cfg["era_end"])
    annual_antarctic = annual_antarctic[
        (annual_antarctic["year"] >= era_a0) & (annual_antarctic["year"] <= era_a1)
    ].reset_index(drop=True)
    trend_antarctic = compute_trend(
        annual_antarctic, boot_n, boot_conf, boot_seed, doy_column="breakup_doy"
    )
    mk_antarctic = mann_kendall_pvalue(annual_antarctic["breakup_doy"].to_numpy())

    # ── Tables ──────────────────────────────────────────────────────────────
    annual_arctic.to_csv(tables_dir / "arctic_annual_minimum_doy_osisaf_sia.csv", index=False)
    annual_ext.to_csv(tables_dir / "arctic_annual_minimum_doy_nsidc_extent.csv", index=False)
    annual_antarctic.to_csv(tables_dir / "antarctic_annual_breakup_doy_afin.csv", index=False)
    surveys.to_csv(tables_dir / "antarctic_afin_all_surveys.csv", index=False)

    # ── Figures ─────────────────────────────────────────────────────────────
    arctic_fig = cfg["plot"]["arctic_figure"]
    ant_fig = cfg["plot"]["antarctic_figure"]
    combo_fig = cfg["plot"]["combined_figure"]

    plot_doy_trend(
        annual_arctic,
        "minimum_doy",
        trend_arctic,
        figures_dir / arctic_fig,
        f"Arctic SIA annual minimum timing ({trend_arctic.year_start}–{trend_arctic.year_end})",
        "OSI SAF daily SIA minimum",
        "Day of year of annual SIA minimum",
        ylim=(220, 290),
        ref_doy=255,
        ref_label="Mid-Sep. reference",
        dpi=dpi,
    )
    plot_doy_trend(
        annual_antarctic,
        "breakup_doy",
        trend_antarctic,
        figures_dir / ant_fig,
        f"Antarctic fast-ice breakup proxy — Atka Bay AFIN ({era_a0}–{era_a1})",
        "Last in situ AFIN survey (Neumayer III)",
        "Day of year of last fast-ice survey",
        color="#0e6655",
        ylim=(160, 380),
        ref_doy=15,
        ref_label="Mid-Jan. reference",
        dpi=dpi,
    )
    plot_polar_comparison(
        annual_arctic,
        trend_arctic,
        annual_antarctic,
        trend_antarctic,
        figures_dir / combo_fig,
        str(cutoff.date()),
        dpi=dpi,
    )

    summary = {
        "analysis_reference": cfg["project"]["analysis_reference"],
        "data_cutoff": str(cutoff.date()),
        "author": cfg["project"].get("author", ""),
        "arctic": {
            "question": "Has the day-of-year of the Arctic SIA annual minimum shifted?",
            "last_complete_minimum_year": last_arctic_year,
            "product": "EUMETSAT OSI SAF Sea Ice Index v3.0 (NH SIA)",
            "doi": "10.15770/EUM_SAF_OSI_0023",
            "trend": _trend_block(trend_arctic, mk_arctic, alpha),
            "nsidc_extent_sensitivity": _trend_block(trend_ext, None, alpha),
            "figure": str(Path(cfg["paths"]["figures_dir"]) / arctic_fig),
        },
        "antarctic": {
            "question": "Has the day-of-year of Atka Bay fast-ice breakup shifted?",
            "station": ant_cfg["station"],
            "network": ant_cfg["network"],
            "context": "SPOT emperor penguin observatory ~8 km from Neumayer III",
            "method": "Last AFIN transect survey date per austral season (PANGAEA 2010–2018)",
            "pangaea_bibliography": "10.1594/PANGAEA.908860",
            "era": f"{era_a0}–{era_a1}",
            "trend": _trend_block(trend_antarctic, mk_antarctic, alpha),
            "figure": str(Path(cfg["paths"]["figures_dir"]) / ant_fig),
        },
        "combined_figure": str(Path(cfg["paths"]["figures_dir"]) / combo_fig),
        "generated_at": pd.Timestamp.now(tz="UTC").isoformat(),
    }

    with (results_dir / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    ta, tb = trend_arctic, trend_antarctic
    print("=" * 64)
    print("Polar sea-ice timing analysis |", cfg["project"]["analysis_reference"])
    print(f"Data cutoff: {cutoff.date()}")
    print("=" * 64)
    print("ARCTIC (OSI SAF SIA minimum DOY)")
    print(f"  {ta.year_start}–{ta.year_end} | slope {ta.slope_days_per_year:+.3f} d/yr | p={ta.p_value:.4f}")
    print("ANTARCTIC (AFIN last survey DOY, Atka Bay / Neumayer III)")
    print(f"  {tb.year_start}–{tb.year_end} | slope {tb.slope_days_per_year:+.3f} d/yr | p={tb.p_value:.4f}")
    print(f"Combined figure: {figures_dir / combo_fig}")

    subprocess.run([sys.executable, str(ROOT / "scripts" / "update_docs.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_latex.py")], check=True)


if __name__ == "__main__":
    main()
