#!/usr/bin/env python3
"""Phase 2 spatial exploration: Pearson-r heat map + early/late tercile composite."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from matplotlib.patches import Rectangle
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.gridded_sic import find_monthly_file, get_crop_slices, load_config, load_monthly_sic

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
except ImportError as exc:
    raise SystemExit("cartopy is required: pip install cartopy") from exc

# Approximate sub-region boxes (lon_min, lon_max, lat_min, lat_max) for annotation
REGION_BOXES = {
    "Beaufort": (-150, -120, 70, 78),
    "Kara": (55, 90, 70, 82),
    "MIZ": (-30, 30, 72, 82),
}


def load_doy_series() -> pd.DataFrame:
    path = ROOT / "results/tables/arctic_annual_minimum_doy_osisaf_sia.csv"
    df = pd.read_csv(path)
    return df[df["minimum_value_mkm2"] > 0][["year", "minimum_doy"]].copy()


def load_july_sic_stack(
    data_dir: Path, years: list[int]
) -> tuple[np.ndarray, np.ndarray]:
    """Return (n_years, H, W) July SIC stack and aligned years array."""
    planes: list[np.ndarray] = []
    kept: list[int] = []
    for year in years:
        fpath = find_monthly_file(data_dir, year, 7)
        if fpath is None:
            continue
        planes.append(load_monthly_sic(fpath))
        kept.append(year)
    if not planes:
        raise FileNotFoundError(f"No July SIC files found in {data_dir}")
    return np.stack(planes, axis=0), np.array(kept, dtype=int)


def pearson_r_map(sic: np.ndarray, doy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Vectorised Pearson r + two-tailed p-value along year axis. sic: (n, H, W), doy: (n,)."""
    n = sic.shape[0]
    x = sic.astype(np.float64)
    y = doy.astype(np.float64)
    x_mean = x.mean(axis=0)
    y_mean = y.mean()
    xc = x - x_mean
    yc = y - y_mean
    num = np.sum(xc * yc[:, None, None], axis=0)
    den = np.sqrt(np.sum(xc**2, axis=0) * np.sum(yc**2))
    with np.errstate(invalid="ignore", divide="ignore"):
        r = num / den
    valid = (np.std(x, axis=0) > 1e-6) & np.isfinite(r)
    r = np.where(valid, r, np.nan).astype(np.float32)

    df = n - 2
    with np.errstate(invalid="ignore", divide="ignore"):
        t_stat = r * np.sqrt(df / np.clip(1 - r**2, 1e-12, None))
        p = 2 * stats.t.sf(np.abs(t_stat), df)
    p = np.where(valid, p, np.nan).astype(np.float32)
    return r, p


def fdr_significance_mask(p_map: np.ndarray, valid_mask: np.ndarray, q: float = 0.05) -> np.ndarray:
    """Benjamini-Hochberg FDR correction over all valid (ocean) grid cells."""
    flat_p = p_map[valid_mask]
    m = flat_p.size
    if m == 0:
        return np.zeros_like(p_map, dtype=bool)
    order = np.argsort(flat_p)
    ranked = flat_p[order]
    thresh_line = (np.arange(1, m + 1) / m) * q
    passing = ranked <= thresh_line
    sig_flat = np.zeros(m, dtype=bool)
    if passing.any():
        cutoff_rank = np.max(np.where(passing)[0])
        sig_flat[order[: cutoff_rank + 1]] = True
    sig_map = np.zeros_like(p_map, dtype=bool)
    sig_map[valid_mask] = sig_flat
    return sig_map


def region_mean_tests(
    sic: np.ndarray, doy: np.ndarray, lat: np.ndarray, lon: np.ndarray
) -> pd.DataFrame:
    """Pearson r/p for each sub-region using the spatially averaged SIC time series.

    Averaging first collapses each region to a single time series, so this is a
    3-hypothesis test rather than ~16,000 pixelwise tests -- the honest way to ask
    whether a named region's July SIC predicts minimum DOY.
    """
    rows = []
    for name, (lon0, lon1, lat0, lat1) in REGION_BOXES.items():
        mask = (lon >= lon0) & (lon <= lon1) & (lat >= lat0) & (lat <= lat1)
        ts = sic[:, mask].mean(axis=1)
        r, p = stats.pearsonr(ts, doy)
        rows.append({"region": name, "n_pixels": int(mask.sum()), "r": r, "p": p, "n_years": len(doy)})
    return pd.DataFrame(rows)


def split_terciles(df: pd.DataFrame) -> tuple[list[int], list[int]]:
    ranked = df.sort_values("minimum_doy")
    n = len(ranked)
    k = n // 3
    early = ranked.iloc[:k]["year"].tolist()
    late = ranked.iloc[-k:]["year"].tolist()
    return early, late


def build_lat_lon_grid() -> tuple[np.ndarray, np.ndarray]:
    """Lat/lon for cropped NSIDC polar-stereo grid."""
    from pyproj import Proj

    sample = next((ROOT / load_config()["data"]["nsidc_cdr_dir"]).glob("sic_psn25_*_v06r00.nc"))
    import xarray as xr

    ys, xs = get_crop_slices()
    with xr.open_dataset(sample) as ds:
        x = ds["x"].isel(x=xs).values
        y = ds["y"].isel(y=ys).values
    xx, yy = np.meshgrid(x, y)
    proj = Proj(
        "+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 "
        "+datum=WGS84 +units=m +no_defs"
    )
    lon, lat = proj(xx, yy, inverse=True)
    lon = np.where(lon > 180, lon - 360, lon)
    return lat.astype(np.float32), lon.astype(np.float32)


def mask_ocean(sic_stack: np.ndarray) -> np.ndarray:
    """Pixels that ever had SIC > 1% in July."""
    return np.nanmax(sic_stack, axis=0) > 0.01


def plot_spatial_heatmap(
    r_map: np.ndarray,
    delta_map: np.ndarray,
    lat: np.ndarray,
    lon: np.ndarray,
    ocean_mask: np.ndarray,
    early_years: list[int],
    late_years: list[int],
    mean_july_sic: np.ndarray,
    out_path: Path,
    dpi: int,
    sig_mask: np.ndarray | None = None,
    n_sig_fdr: int = 0,
) -> None:
    proj = ccrs.NorthPolarStereo(central_longitude=-45)
    fig, axes = plt.subplots(
        1, 2, figsize=(11, 5.5), subplot_kw={"projection": proj}, layout="constrained"
    )

    r_plot = np.where(ocean_mask, r_map, np.nan)
    d_plot = np.where(ocean_mask, delta_map, np.nan)

    for ax, data, title, cmap, vmin, vmax in [
        (axes[0], r_plot, "Pearson r: July SIC vs min DOY", "RdBu_r", -1, 1),
        (axes[1], d_plot, "ΔSIC: early − late tercile (July)", "RdBu_r", None, None),
    ]:
        ax.set_extent([-180, 180, 55, 90], crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.LAND, facecolor="#e8e8e8", edgecolor="none", zorder=0)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.4, zorder=2)
        ax.gridlines(draw_labels=False, linewidth=0.2, alpha=0.4)

        if vmin is None:
            masked = data[ocean_mask] if ocean_mask is not None else data.ravel()
            masked = masked[np.isfinite(masked)]
            lim = float(np.percentile(np.abs(masked), 98)) if masked.size else 0.05
            lim = max(lim, 1e-4)
            vmin, vmax = -lim, lim

        im = ax.pcolormesh(
            lon, lat, data, transform=ccrs.PlateCarree(),
            cmap=cmap, vmin=vmin, vmax=vmax, shading="auto", zorder=1,
        )
        ax.contour(
            lon, lat, mean_july_sic, levels=[0.15], colors="k",
            linewidths=0.8, transform=ccrs.PlateCarree(), zorder=3,
        )
        for name, (lon0, lon1, lat0, lat1) in REGION_BOXES.items():
            w = lon1 - lon0
            h = lat1 - lat0
            ax.add_patch(
                Rectangle(
                    (lon0, lat0), w, h, fill=False, edgecolor="gold",
                    linewidth=1.2, transform=ccrs.PlateCarree(), zorder=4,
                )
            )
            ax.text(
                lon0 + w / 2, lat1 + 0.5, name, transform=ccrs.PlateCarree(),
                ha="center", va="bottom", fontsize=7, color="goldenrod", fontweight="bold",
            )
        ax.set_title(title, fontsize=10)
        fig.colorbar(im, ax=ax, shrink=0.72, pad=0.02)

    if sig_mask is not None and n_sig_fdr > 0:
        ys_idx, xs_idx = np.where(sig_mask)
        axes[0].scatter(
            lon[ys_idx, xs_idx], lat[ys_idx, xs_idx], s=1.5, color="black",
            marker=".", transform=ccrs.PlateCarree(), zorder=5,
            label=f"FDR-significant (q<0.05, n={n_sig_fdr})",
        )
        axes[0].legend(loc="lower left", fontsize=6, framealpha=0.9)

    caption = (
        f"No pixel survives Benjamini–Hochberg FDR correction (q=0.05) across "
        f"{int(ocean_mask.sum())} ocean cells." if n_sig_fdr == 0 else
        f"{n_sig_fdr} of {int(ocean_mask.sum())} ocean cells survive FDR correction (q=0.05)."
    )
    fig.suptitle(
        f"Spatial structure of Arctic minimum-DOY variability "
        f"(early tercile n={len(early_years)}, late tercile n={len(late_years)})\n"
        f"{caption} Colours show uncorrected pixel-wise r; interpret with caution.",
        fontweight="bold", fontsize=10,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    cfg = load_config()
    data_dir = ROOT / cfg["data"]["nsidc_cdr_dir"]
    y0, y1 = cfg["data"]["arctic_subset_years"]
    dpi = int(cfg["plot"]["dpi"])
    tables_dir = ROOT / cfg["paths"]["tables_dir"] / "spatial"
    figures_dir = ROOT / cfg["paths"]["figures_dir"]

    doy_df = load_doy_series()
    doy_df = doy_df[(doy_df["year"] >= y0) & (doy_df["year"] <= y1)].copy()
    early_years, late_years = split_terciles(doy_df)

    sic_stack, years = load_july_sic_stack(data_dir, list(range(y0, y1 + 1)))
    valid_years = set(doy_df["year"])
    keep = np.isin(years, list(valid_years))
    sic_stack = sic_stack[keep]
    years = years[keep]
    label_df = doy_df.set_index("year").loc[years]
    doy = label_df["minimum_doy"].values

    r_map, p_map = pearson_r_map(sic_stack, doy)
    early_idx = np.isin(years, early_years)
    late_idx = np.isin(years, late_years)
    delta_map = sic_stack[early_idx].mean(axis=0) - sic_stack[late_idx].mean(axis=0)
    mean_july_sic = sic_stack.mean(axis=0)
    lat, lon = build_lat_lon_grid()
    ocean_mask = mask_ocean(sic_stack)

    valid_mask = ocean_mask & np.isfinite(r_map)
    sig_mask = fdr_significance_mask(p_map, valid_mask, q=0.05)
    n_sig_fdr = int(sig_mask.sum())
    n_nominal = int(((np.abs(r_map) > 0) & (p_map < 0.05) & valid_mask).sum())
    n_valid = int(valid_mask.sum())

    region_df = region_mean_tests(sic_stack, doy, lat, lon)

    tables_dir.mkdir(parents=True, exist_ok=True)
    np.save(tables_dir / "r_map.npy", r_map)
    np.save(tables_dir / "p_map.npy", p_map)
    np.save(tables_dir / "delta_sic_map.npy", delta_map)
    region_df.to_csv(tables_dir / "region_mean_tests.csv", index=False)

    meta = {
        "early_tercile_years": early_years,
        "late_tercile_years": late_years,
        "n_years": int(len(years)),
        "year_range": [int(years.min()), int(years.max())],
        "mean_r_ocean": float(np.nanmean(r_map)),
        "n_valid_ocean_cells": n_valid,
        "n_nominal_p_lt_0.05_uncorrected": n_nominal,
        "n_significant_after_fdr_q0.05": n_sig_fdr,
        "expected_false_positives_at_alpha_0.05": round(0.05 * n_valid, 1),
        "region_mean_tests": region_df.to_dict(orient="records"),
        "interpretation": (
            "Pixel-wise correlations do not survive multiple-comparison correction; "
            "region-averaged tests (see region_mean_tests.csv) are the statistically "
            "defensible summary."
        ),
    }
    (tables_dir / "tercile_metadata.json").write_text(json.dumps(meta, indent=2))

    fig_path = figures_dir / cfg["plot"]["spatial_heatmap_figure"]
    plot_spatial_heatmap(
        r_map, delta_map, lat, lon, ocean_mask,
        early_years, late_years, mean_july_sic, fig_path, dpi,
        sig_mask=sig_mask, n_sig_fdr=n_sig_fdr,
    )
    print(f"Early tercile ({len(early_years)} yrs): {early_years[:3]}…{early_years[-3:]}")
    print(f"Late tercile ({len(late_years)} yrs): {late_years[:3]}…{late_years[-3:]}")
    print(f"\nSignificance check ({n_valid} ocean cells, n={len(doy)} years):")
    print(f"  Nominal (uncorrected, alpha=0.05): {n_nominal} cells "
          f"(chance expectation: {0.05 * n_valid:.0f})")
    print(f"  Surviving Benjamini-Hochberg FDR (q=0.05): {n_sig_fdr} cells")
    print("\nRegion-averaged tests (honest, 3-hypothesis, no pixel multiplicity):")
    print(region_df.to_string(index=False))
    print(f"\nr_map / p_map saved: {tables_dir}")
    print(f"Fig 5 saved: {fig_path}")


if __name__ == "__main__":
    main()
