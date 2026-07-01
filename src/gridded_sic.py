"""Load NSIDC CDRv6 monthly Arctic SIC grids for Phase 2 spatial analysis."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr
import yaml
from pyproj import Proj

ROOT = Path(__file__).resolve().parents[1]


def load_config() -> dict:
    with (ROOT / "config.yaml").open() as f:
        return yaml.safe_load(f)


def _arctic_crop_slices(lat_min: float = 60.0, grid_size: int = 160) -> tuple[slice, slice]:
    """Return y/x slices for lat >= lat_min, center-cropped to grid_size."""
    sample = next((ROOT / load_config()["data"]["nsidc_cdr_dir"]).glob("sic_psn25_*_v06r00.nc"))
    ds = xr.open_dataset(sample)
    x = ds["x"].values
    y = ds["y"].values
    ds.close()
    xx, yy = np.meshgrid(x, y)
    proj = Proj(
        "+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 "
        "+datum=WGS84 +units=m +no_defs"
    )
    _, lat = proj(xx, yy, inverse=True)
    rows, cols = np.where(lat >= lat_min)
    r0, r1 = int(rows.min()), int(rows.max()) + 1
    c0, c1 = int(cols.min()), int(cols.max()) + 1
    ch, cw = (r1 - r0), (c1 - c0)
    cr = r0 + (ch - grid_size) // 2
    cc = c0 + (cw - grid_size) // 2
    return slice(cr, cr + grid_size), slice(cc, cc + grid_size)


_CROP_CACHE: tuple[slice, slice] | None = None


def get_crop_slices() -> tuple[slice, slice]:
    global _CROP_CACHE
    if _CROP_CACHE is None:
        cfg = load_config()
        _CROP_CACHE = _arctic_crop_slices(
            lat_min=float(cfg["data"]["arctic_lat_min"]),
            grid_size=int(cfg["data"]["grid_size"]),
        )
    return _CROP_CACHE


def load_monthly_sic(path: Path) -> np.ndarray:
    """Load one monthly SIC field, cropped to Arctic cap (values 0–1).

    NOTE: NSIDC CDRv6 (v06r00) stores ``cdr_seaice_conc_monthly`` already as a
    unitless 0-1 fraction (units="1", no percent scaling, no legacy flag values
    mixed in -- verified empirically across 1979/2020/2025 sample files). Do NOT
    divide by 100 here; older CDR versions (v3/v4) used a 0-100 percent scale
    with sentinel flag values, but v06r00 does not.
    """
    ys, xs = get_crop_slices()
    with xr.open_dataset(path) as ds:
        sic = ds["cdr_seaice_conc_monthly"].isel(time=0, y=ys, x=xs).values.astype(np.float32)
    sic = np.nan_to_num(sic, nan=0.0)
    return np.clip(sic, 0.0, 1.0)


def find_monthly_file(data_dir: Path, year: int, month: int) -> Path | None:
    pattern = f"sic_psn25_{year}{month:02d}_"
    matches = sorted(data_dir.glob(f"{pattern}*_v06r00.nc"))
    return matches[0] if matches else None
