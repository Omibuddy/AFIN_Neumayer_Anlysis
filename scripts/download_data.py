#!/usr/bin/env python3
"""Download official datasets: Arctic indices + AFIN PANGAEA (Atka Bay)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.load_afin import download_pangaea_dataset

URLS = {
    "data/raw/osisaf/ice_area_nh_sii-v3p0_daily.txt": (
        "ftp://osisaf.met.no/prod/ice/index/v3p0/timeseries/nh/ice_area_nh_sii-v3p0_daily.txt"
    ),
    "data/raw/nsidc/N_seaice_extent_daily_v4.0.csv": (
        "https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v4.0.csv"
    ),
}


def download_url(rel_path: str, url: str) -> None:
    dest = ROOT / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {rel_path} …")
    subprocess.run(["curl", "-sL", "-o", str(dest), url], check=True)
    print(f"  -> {dest.stat().st_size / 1024:.1f} KB")


def main() -> None:
    for rel, url in URLS.items():
        download_url(rel, url)

    with (ROOT / "config.yaml").open() as f:
        cfg = yaml.safe_load(f)
    afin_dir = ROOT / cfg["paths"]["afin_dir"]
    for year, doi in cfg["antarctic"]["pangaea_dois"].items():
        dest = afin_dir / f"atka_bay_afin_{year}.txt"
        if dest.exists():
            print(f"Skip AFIN {year} (exists)")
            continue
        print(f"Downloading AFIN {year} from PANGAEA …")
        download_pangaea_dataset(doi, dest)
        print(f"  -> {dest.stat().st_size / 1024:.1f} KB")

    print("Done. Run: python scripts/run_analysis.py")


if __name__ == "__main__":
    main()
