"""Figures for polar sea-ice timing trends."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.statistics import TrendResult


def _trend_panel(
    ax: plt.Axes,
    annual: pd.DataFrame,
    doy_col: str,
    trend: TrendResult,
    scatter_label: str,
    ylabel: str,
    color: str,
    ref_doy: float | None,
    ref_label: str | None,
) -> None:
    years = annual["year"].to_numpy(dtype=float)
    doy = annual[doy_col].to_numpy(dtype=float)
    y_fit = trend.slope_days_per_year * years + trend.intercept

    ax.scatter(
        years,
        doy,
        s=42,
        color=color,
        edgecolors="white",
        linewidths=0.5,
        zorder=3,
        label=scatter_label,
    )
    ax.plot(years, y_fit, color="#c0392b", linewidth=2.0, label="OLS trend", zorder=2)
    y_lo = trend.ci_lower * years + trend.intercept
    y_hi = trend.ci_upper * years + trend.intercept
    ax.fill_between(years, y_lo, y_hi, color="#c0392b", alpha=0.15)

    if ref_doy is not None and ref_label:
        ax.axhline(ref_doy, color="#7f8c8d", linestyle="--", linewidth=0.9, alpha=0.7)
        ax.text(years.min() + 0.3, ref_doy + 1.2, ref_label, fontsize=7, color="#7f8c8d")

    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=7)

    stats = (
        f"n = {trend.n_years} ({trend.year_start}–{trend.year_end})\n"
        f"slope = {trend.slope_days_per_year:+.2f} d yr$^{{-1}}$ "
        f"({trend.slope_days_per_year * 10:+.1f} d decade$^{{-1}}$)\n"
        f"p = {trend.p_value:.3f}, r = {trend.r_value:.2f}"
    )
    ax.text(
        0.03,
        0.97,
        stats,
        transform=ax.transAxes,
        fontsize=7,
        va="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="#ccc"),
    )


def plot_doy_trend(
    annual: pd.DataFrame,
    doy_col: str,
    trend: TrendResult,
    output_path: Path,
    title: str,
    scatter_label: str,
    ylabel: str,
    color: str = "#1f4e79",
    ylim: tuple[float, float] | None = None,
    ref_doy: float | None = None,
    ref_label: str | None = None,
    dpi: int = 300,
) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.2), layout="constrained")
    _trend_panel(ax, annual, doy_col, trend, scatter_label, ylabel, color, ref_doy, ref_label)
    ax.set_title(title, fontsize=11, fontweight="bold")
    if ylim:
        ax.set_ylim(*ylim)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def plot_polar_comparison(
    arctic_annual: pd.DataFrame,
    arctic_trend: TrendResult,
    antarctic_annual: pd.DataFrame,
    antarctic_trend: TrendResult,
    output_path: Path,
    cutoff_date: str,
    dpi: int = 300,
) -> None:
    """Side-by-side Arctic minimum vs Antarctic fast-ice breakup timing."""
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), layout="constrained")

    _trend_panel(
        axes[0],
        arctic_annual,
        "minimum_doy",
        arctic_trend,
        "Arctic SIA minimum (OSI SAF)",
        "Day of year",
        "#1f4e79",
        255,
        "Mid-Sep. ref.",
    )
    axes[0].set_title(
        f"Arctic — annual sea-ice area minimum\n({arctic_trend.year_start}–{arctic_trend.year_end})",
        fontsize=10,
        fontweight="bold",
    )
    axes[0].set_ylim(220, 290)

    _trend_panel(
        axes[1],
        antarctic_annual.assign(minimum_doy=antarctic_annual["breakup_doy"]),
        "minimum_doy",
        antarctic_trend,
        "Atka Bay last AFIN survey",
        "Day of year",
        "#0e6655",
        15,
        "Mid-Jan. ref.",
    )
    axes[1].set_title(
        f"Antarctic — fast-ice breakup proxy (AFIN / Neumayer III)\n"
        f"({antarctic_trend.year_start}–{antarctic_trend.year_end})",
        fontsize=10,
        fontweight="bold",
    )
    axes[1].set_ylim(160, 380)

    fig.suptitle(
        f"Polar sea-ice timing trends (data through {cutoff_date})",
        fontsize=12,
        fontweight="bold",
        y=1.02,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
