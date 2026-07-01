#!/usr/bin/env python3
"""Phase 1 extension: amount-vs-timing sensitivity figures (Figs 2–3)."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.load_data import (
    annual_minimum_doy,
    last_complete_minimum_year,
    load_osisaf_daily_sia,
)


def load_config() -> dict:
    with (ROOT / "config.yaml").open() as f:
        return yaml.safe_load(f)


def fig2_dual_axis(annual: pd.DataFrame, out_path: Path, dpi: int) -> None:
    """SIA at minimum vs min-DOY dual-axis — magnitude loss ≠ calendar shift."""
    valid = annual[annual["minimum_value_mkm2"] > 0].copy()
    fig, ax1 = plt.subplots(figsize=(8, 4.2), layout="constrained")

    color_doy = "#1f4e79"
    color_sia = "#c0392b"
    ax1.plot(valid["year"], valid["minimum_doy"], "o-", color=color_doy, linewidth=1.5, label="Min DOY")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Minimum DOY", color=color_doy)
    ax1.tick_params(axis="y", labelcolor=color_doy)
    ax1.set_ylim(220, 280)

    ax2 = ax1.twinx()
    ax2.plot(valid["year"], valid["minimum_value_mkm2"], "s--", color=color_sia, linewidth=1.5, label="SIA at min")
    ax2.set_ylabel("SIA at minimum (M km²)", color=color_sia)
    ax2.tick_params(axis="y", labelcolor=color_sia)

    slope_doy, _, _, p_doy, _ = stats.linregress(valid["year"], valid["minimum_doy"])
    slope_sia, _, _, p_sia, _ = stats.linregress(valid["year"], valid["minimum_value_mkm2"])
    ax1.text(
        0.02, 0.97,
        f"DOY trend: {slope_doy:+.2f} d yr$^{{-1}}$ ($p$={p_doy:.2f})\n"
        f"SIA trend: {slope_sia:+.3f} M km² yr$^{{-1}}$ ($p$={p_sia:.3f})",
        transform=ax1.transAxes, va="top", fontsize=8,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="#ccc"),
    )
    ax1.set_title("Arctic: sea-ice amount vs minimum timing (decoupled trends)")
    ax1.grid(True, alpha=0.25)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def fig3_aug31_scatter(daily: pd.DataFrame, annual: pd.DataFrame, out_path: Path, dpi: int) -> None:
    """Aug 31 hemispheric SIA vs annual minimum DOY scatter."""
    valid = annual[annual["minimum_value_mkm2"] > 0].copy()
    aug31 = daily[(daily["month"] == 8) & (daily["day"] == 31)][["year", "sia_mkm2"]]
    aug31 = aug31.groupby("year", as_index=False).last()
    merged = valid.merge(aug31, on="year", how="inner")

    fig, ax = plt.subplots(figsize=(6, 4.5), layout="constrained")
    ax.scatter(merged["sia_mkm2"], merged["minimum_doy"], s=50, color="#1f4e79", edgecolors="white", linewidths=0.5)
    slope, intercept, r, p, _ = stats.linregress(merged["sia_mkm2"], merged["minimum_doy"])
    x_fit = np.linspace(merged["sia_mkm2"].min(), merged["sia_mkm2"].max(), 100)
    ax.plot(x_fit, slope * x_fit + intercept, color="#c0392b", linewidth=2, label="OLS fit")
    ax.set_xlabel("Aug 31 hemispheric SIA (M km²)")
    ax.set_ylabel("Annual minimum DOY")
    ax.set_title("Pre-melt-season SIA vs minimum timing")
    ax.text(
        0.03, 0.97, f"r = {r:.2f}, p = {p:.3f}, n = {len(merged)}",
        transform=ax.transAxes, va="top", fontsize=8,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="#ccc"),
    )
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    cfg = load_config()
    cutoff = pd.Timestamp(cfg["dates"]["data_cutoff"])
    melt_start = int(cfg["dates"]["arctic_melt_month_start"])
    melt_end = int(cfg["dates"]["arctic_melt_month_end"])
    arctic_start = int(cfg["dates"]["arctic_era_start"])
    dpi = int(cfg["plot"]["dpi"])
    figures_dir = ROOT / cfg["paths"]["figures_dir"]

    daily = load_osisaf_daily_sia(ROOT / cfg["paths"]["osisaf_daily_sia"], cutoff)
    last_year = last_complete_minimum_year(cutoff, melt_end)
    annual = annual_minimum_doy(daily, "sia_mkm2", melt_start, melt_end, last_year)
    annual = annual[annual["year"] >= arctic_start].reset_index(drop=True)

    fig2_path = figures_dir / cfg["plot"]["sensitivity_figure"]
    fig3_path = figures_dir / cfg["plot"]["aug31_scatter_figure"]
    fig2_dual_axis(annual, fig2_path, dpi)
    fig3_aug31_scatter(daily, annual, fig3_path, dpi)
    print(f"Fig 2 saved: {fig2_path}")
    print(f"Fig 3 saved: {fig3_path}")


if __name__ == "__main__":
    main()
