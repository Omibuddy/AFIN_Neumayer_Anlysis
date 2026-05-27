"""Trend estimation and significance testing."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass
class TrendResult:
    slope_days_per_year: float
    intercept: float
    r_value: float
    p_value: float
    std_err: float
    ci_lower: float
    ci_upper: float
    theil_sen_slope: float
    theil_sen_ci_lower: float
    theil_sen_ci_upper: float
    n_years: int
    year_start: int
    year_end: int
    mean_doy: float
    std_doy: float


def linear_trend(years: np.ndarray, doy: np.ndarray) -> tuple[float, float, float, float, float]:
    slope, intercept, r, p, se = stats.linregress(years, doy)
    return float(slope), float(intercept), float(r), float(p), float(se)


def bootstrap_slope_ci(
    years: np.ndarray,
    doy: np.ndarray,
    n_iter: int,
    confidence: float,
    seed: int,
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    slopes = np.empty(n_iter)
    n = len(years)
    for i in range(n_iter):
        idx = rng.integers(0, n, size=n)
        slopes[i], *_ = stats.linregress(years[idx], doy[idx])
    alpha = (1.0 - confidence) / 2.0
    return float(np.quantile(slopes, alpha)), float(np.quantile(slopes, 1.0 - alpha))


def mann_kendall_pvalue(doy: np.ndarray) -> float | None:
    """Non-parametric monotonic trend test (two-sided p-value)."""
    try:
        import pymannkendall as mk  # type: ignore

        return float(mk.original_test(doy).p)
    except ImportError:
        return None


def compute_trend(
    annual: "pd.DataFrame",
    bootstrap_iterations: int,
    confidence: float,
    seed: int,
    doy_column: str = "minimum_doy",
) -> TrendResult:
    import pandas as pd

    if not isinstance(annual, pd.DataFrame):
        raise TypeError("annual must be a pandas DataFrame")

    years = annual["year"].to_numpy(dtype=float)
    doy = annual[doy_column].to_numpy(dtype=float)
    slope, intercept, r, p, se = linear_trend(years, doy)
    ci_lo, ci_hi = bootstrap_slope_ci(
        years, doy, bootstrap_iterations, confidence, seed
    )
    ts_slope, _, ts_lo, ts_hi = stats.theilslopes(doy, years)
    return TrendResult(
        slope_days_per_year=slope,
        intercept=intercept,
        r_value=r,
        p_value=p,
        std_err=se,
        ci_lower=ci_lo,
        ci_upper=ci_hi,
        theil_sen_slope=float(ts_slope),
        theil_sen_ci_lower=float(ts_lo),
        theil_sen_ci_upper=float(ts_hi),
        n_years=len(annual),
        year_start=int(annual["year"].min()),
        year_end=int(annual["year"].max()),
        mean_doy=float(doy.mean()),
        std_doy=float(doy.std(ddof=1)),
    )
