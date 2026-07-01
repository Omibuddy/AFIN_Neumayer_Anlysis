#!/usr/bin/env python3
"""Antarctic AFIN survey calendar figure (Fig 7)."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.load_afin import load_all_afin_years


def load_config() -> dict:
    with (ROOT / "config.yaml").open() as f:
        return yaml.safe_load(f)


def plot_antarctic_calendar(
    surveys: pd.DataFrame,
    annual: pd.DataFrame,
    out_path: Path,
    dpi: int,
) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5), layout="constrained")

    for year, grp in surveys.groupby("year"):
        doys = grp["survey_date"].dt.dayofyear
        ax.scatter([year] * len(doys), doys, s=35, color="#0e6655", alpha=0.7, zorder=2)
        last = annual.loc[annual["year"] == year, "breakup_doy"].iloc[0]
        ax.scatter(year, last, s=120, facecolors="none", edgecolors="#c0392b", linewidths=2, zorder=3)

    # Iceberg-blocking annotations (Arndt et al. 2020)
    for year, label, yoff in [(2013, "Iceberg\nblocking", 0), (2016, "Iceberg\nblocking", 0)]:
        if year in annual["year"].values:
            y = annual.loc[annual["year"] == year, "breakup_doy"].iloc[0]
            ax.annotate(
                label, (year, y), textcoords="offset points", xytext=(12, 20 + yoff),
                fontsize=7, color="#7d3c98",
                arrowprops=dict(arrowstyle="->", color="#7d3c98", lw=0.8),
            )

    ax.set_xlabel("Year")
    ax.set_ylabel("Day of year")
    ax.set_title("Antarctic AFIN survey calendar — Atka Bay (Neumayer III), 2010–2018")
    ax.set_xlim(2009.5, 2018.5)
    ax.set_ylim(150, 380)
    ax.grid(True, alpha=0.25)

    legend_handles = [
        mpatches.Patch(color="#0e6655", label="Individual surveys"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="none",
                   markeredgecolor="#c0392b", markersize=10, markeredgewidth=2, label="Last survey (breakup proxy)"),
    ]
    ax.legend(handles=legend_handles, loc="upper left", fontsize=8)

    ax.text(
        0.98, 0.02,
        "Context: WMO 2025 reports four consecutive record-low\n"
        "Antarctic sea-ice minima (2021–2024). AFIN n=9 years;\n"
        "fast-ice proxy ≠ pan-hemispheric pack ice.",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=7,
        bbox=dict(boxstyle="round", facecolor="#fef9e7", alpha=0.95, edgecolor="#ccc"),
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    cfg = load_config()
    ant_cfg = cfg["antarctic"]
    dois = {int(k): v for k, v in ant_cfg["pangaea_dois"].items()}
    surveys, annual = load_all_afin_years(
        ROOT / cfg["paths"]["afin_dir"], dois, download_missing=False
    )
    era_a0, era_a1 = int(ant_cfg["era_start"]), int(ant_cfg["era_end"])
    surveys = surveys[(surveys["year"] >= era_a0) & (surveys["year"] <= era_a1)]
    annual = annual[(annual["year"] >= era_a0) & (annual["year"] <= era_a1)]

    out_path = ROOT / cfg["paths"]["figures_dir"] / cfg["plot"]["antarctic_calendar_figure"]
    plot_antarctic_calendar(surveys, annual, out_path, int(cfg["plot"]["dpi"]))
    print(f"Fig 7 saved: {out_path}")


if __name__ == "__main__":
    main()
