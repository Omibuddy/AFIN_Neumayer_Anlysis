#!/usr/bin/env python3
"""Download NSIDC CDRv6 G02202 monthly Arctic SIC (May–Jul) for Phase 2 spatial analysis."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
MONTHS = (5, 6, 7)
FILE_RE = re.compile(r"href=\"(sic_psn25_(\d{6})_[^\"]+_v06r00\.nc)\"")


def load_config() -> dict:
    with (ROOT / "config.yaml").open() as f:
        return yaml.safe_load(f)


def discover_monthly_files(base_url: str) -> dict[str, str]:
    """Map YYYYMM -> filename from NOAA@NSIDC directory listing."""
    resp = requests.get(base_url.rstrip("/") + "/", timeout=60)
    resp.raise_for_status()
    mapping: dict[str, str] = {}
    for fname, yyyymm in FILE_RE.findall(resp.text):
        mapping[yyyymm] = fname
    return mapping


def needed_periods(year_start: int, year_end: int) -> list[str]:
    periods: list[str] = []
    for year in range(year_start, year_end + 1):
        for month in MONTHS:
            periods.append(f"{year}{month:02d}")
    return periods


def download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 100_000:
        return
    with requests.get(url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with dest.open("wb") as handle:
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    handle.write(chunk)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Re-download existing files")
    args = parser.parse_args()

    cfg = load_config()
    data_cfg = cfg["data"]
    dest_dir = ROOT / data_cfg["nsidc_cdr_dir"]
    base_url = data_cfg["nsidc_cdr_base_url"]
    y0, y1 = data_cfg["arctic_subset_years"]

    print(f"Discovering CDRv6 monthly files at {base_url} …")
    catalog = discover_monthly_files(base_url)
    periods = needed_periods(y0, y1)
    missing = [p for p in periods if p not in catalog]
    if missing:
        print(f"Warning: {len(missing)} periods not in catalog (e.g. {missing[:5]})")

    downloaded = skipped = 0
    for period in periods:
        fname = catalog.get(period)
        if not fname:
            continue
        dest = dest_dir / fname
        if args.force and dest.exists():
            dest.unlink()
        if dest.exists():
            skipped += 1
            continue
        url = f"{base_url.rstrip('/')}/{fname}"
        print(f"  {fname}")
        download_file(url, dest)
        downloaded += 1

    n_files = len(list(dest_dir.glob("sic_psn25_*_v06r00.nc")))
    print(f"Done: {downloaded} downloaded, {skipped} skipped, {n_files} total in {dest_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
