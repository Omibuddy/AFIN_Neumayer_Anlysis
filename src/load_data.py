"""Load official sea-ice time series used in the analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_osisaf_daily_sia(path: Path, cutoff: pd.Timestamp) -> pd.DataFrame:
    """Load OSI SAF Northern Hemisphere daily sea-ice area (km² → M km²)."""
    rows: list[dict] = []
    with path.open() as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            date = pd.Timestamp(int(parts[1]), int(parts[2]), int(parts[3]))
            if date > cutoff:
                continue
            rows.append(
                {
                    "date": date,
                    "year": int(parts[1]),
                    "month": int(parts[2]),
                    "day": int(parts[3]),
                    "sia_mkm2": float(parts[4]) / 1e6,
                    "source": parts[5] if len(parts) > 5 else "",
                }
            )
    df = pd.DataFrame(rows)
    df["doy"] = df["date"].dt.dayofyear
    return df.sort_values("date").reset_index(drop=True)


def load_nsidc_daily_extent(path: Path, cutoff: pd.Timestamp) -> pd.DataFrame:
    """Load NSIDC Sea Ice Index daily Northern Hemisphere extent."""
    df = pd.read_csv(path, skiprows=[1])
    df.columns = [c.strip() for c in df.columns]
    df["date"] = pd.to_datetime(
        {"year": df["Year"], "month": df["Month"], "day": df["Day"]}
    )
    df = df[df["date"] <= cutoff].copy()
    df["doy"] = df["date"].dt.dayofyear
    df = df.rename(columns={"Extent": "extent_mkm2", "Year": "year", "Month": "month"})
    return df.sort_values("date").reset_index(drop=True)


def annual_minimum_doy(
    daily: pd.DataFrame,
    value_col: str,
    melt_start: int,
    melt_end: int,
    last_complete_year: int,
) -> pd.DataFrame:
    """Per-year day-of-year at which the melt-season minimum occurs."""
    melt = daily[
        (daily["month"] >= melt_start)
        & (daily["month"] <= melt_end)
        & (daily["year"] <= last_complete_year)
    ]
    idx = melt.groupby("year")[value_col].idxmin()
    annual = melt.loc[idx].copy()
    annual = annual.rename(columns={value_col: "minimum_value_mkm2"})
    annual["minimum_doy"] = annual["doy"]
    annual["minimum_date"] = annual["date"]
    return annual[
        ["year", "minimum_doy", "minimum_date", "minimum_value_mkm2"]
    ].sort_values("year").reset_index(drop=True)


def last_complete_minimum_year(cutoff: pd.Timestamp, melt_end_month: int) -> int:
    """
    Last calendar year with a full melt-season minimum before the cutoff.

    As of April 2026 the 2026 melt minimum has not yet occurred, so 2025 is used.
    """
    if cutoff.month < melt_end_month:
        return cutoff.year - 1
    return cutoff.year
