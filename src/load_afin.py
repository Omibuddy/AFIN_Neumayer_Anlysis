"""Load AFIN / Atka Bay fast-ice surveys from PANGAEA (Neumayer III)."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd


def download_pangaea_dataset(doi_suffix: str, dest: Path) -> None:
    """Download tab-delimited data from PANGAEA via curl (robust on macOS)."""
    import subprocess

    dest.parent.mkdir(parents=True, exist_ok=True)
    # Prefer doi.pangaea.de to avoid HTML landing pages on some setups.
    doi = doi_suffix.strip()
    # Accept either "PANGAEA.XXXXXX" or full DOI "10.1594/PANGAEA.XXXXXX".
    if doi.startswith("https://doi.org/"):
        doi = doi.removeprefix("https://doi.org/").strip()
    if doi.startswith("http://doi.org/"):
        doi = doi.removeprefix("http://doi.org/").strip()
    if doi.startswith("10.1594/"):
        doi = doi.removeprefix("10.1594/").strip()

    url = f"https://doi.pangaea.de/10.1594/{doi}"
    subprocess.run(
        [
            "curl",
            "-sL",
            "-A",
            "curl/8",
            "-H",
            "Accept: text/tab-separated-values",
            "-o",
            str(dest),
            url,
        ],
        check=True,
    )


def _find_data_start(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        # Newer format: starts with an Event column
        if line.startswith("Event\t") and "Date/Time" in line:
            return i
        # Older format (e.g. 2010): first column is the timestamp
        if line.startswith("Date/Time") and "\t" in line:
            return i
    raise ValueError("Could not locate PANGAEA data header row")


def parse_afin_campaign(path: Path, year: int) -> pd.DataFrame:
    """Parse one annual AFIN transect file into a tidy survey table."""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    start = _find_data_start(lines)
    df = pd.read_csv(StringIO("\n".join(lines[start:])), sep="\t", low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]

    # Older years may not include an explicit "Event" column.
    if "Event" not in df.columns:
        if "Sample label" in df.columns:
            df.insert(0, "Event", df["Sample label"])
        else:
            df.insert(0, "Event", "AFIN")

    date_col = next((c for c in df.columns if c.startswith("Date/Time")), df.columns[1])
    df["survey_date"] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=["survey_date"])
    df["year"] = year
    # Total consolidated ice thickness (center hole): sea ice + platelet layer
    ice_col = next((c for c in df.columns if c.startswith("EsEs")), None)
    sipl_col = next((c for c in df.columns if c.startswith("SIPL")), None)
    if ice_col:
        df["sea_ice_thickness_m"] = pd.to_numeric(df[ice_col], errors="coerce")
    if sipl_col:
        df["platelet_thickness_m"] = pd.to_numeric(df[sipl_col], errors="coerce")
    if ice_col and sipl_col:
        df["total_ice_m"] = df["sea_ice_thickness_m"] + df["platelet_thickness_m"].fillna(0)
    t2_col = next((c for c in df.columns if c == "T2 [°C]" or c.startswith("T2")), None)
    if t2_col:
        df["air_temp_2m_c"] = pd.to_numeric(df[t2_col], errors="coerce")

    return df[
        [
            c
            for c in [
                "year",
                "survey_date",
                "Event",
                "sea_ice_thickness_m",
                "platelet_thickness_m",
                "total_ice_m",
                "air_temp_2m_c",
            ]
            if c in df.columns
        ]
    ]


def annual_breakup_from_surveys(surveys: pd.DataFrame) -> pd.DataFrame:
    """
    Last AFIN survey date per year ≈ latest in situ fast-ice observation before breakup.

    Surveys stop when the bay becomes unsafe or ice-free; this proxies breakup timing
  (see Arndt et al. 2020, The Cryosphere).
    """
    rows = []
    for year, grp in surveys.groupby("year"):
        last_date = grp["survey_date"].max()
        last_rows = grp[grp["survey_date"] == last_date]
        rows.append(
            {
                "year": int(year),
                "breakup_date": last_date,
                "breakup_doy": int(last_date.dayofyear),
                "first_survey_date": grp["survey_date"].min(),
                "first_survey_doy": int(grp["survey_date"].min().dayofyear),
                "n_surveys": grp["survey_date"].dt.normalize().nunique(),
                "mean_total_ice_m_last_survey": last_rows["total_ice_m"].mean()
                if "total_ice_m" in last_rows
                else None,
                "mean_air_temp_2m_last_survey": last_rows["air_temp_2m_c"].mean()
                if "air_temp_2m_c" in last_rows
                else None,
            }
        )
    return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)


def load_all_afin_years(
    afin_dir: Path,
    pangaea_dois: dict[int, str],
    download_missing: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load 2010–2018 AFIN campaigns; optionally download missing files."""
    frames: list[pd.DataFrame] = []
    for year, doi in sorted(pangaea_dois.items()):
        dest = afin_dir / f"atka_bay_afin_{year}.txt"
        if dest.exists():
            # Some requests can yield an HTML landing page; detect and refresh.
            head = dest.read_text(encoding="utf-8", errors="ignore")[:200].lstrip()
            if head.startswith("<!DOCTYPE html") or head.startswith("<html"):
                dest.unlink(missing_ok=True)

        if not dest.exists():
            if not download_missing:
                raise FileNotFoundError(f"Missing {dest}; run scripts/download_data.py")
            print(f"  Downloading AFIN {year} from PANGAEA …")
            download_pangaea_dataset(doi, dest)
        frames.append(parse_afin_campaign(dest, year))

    surveys = pd.concat(frames, ignore_index=True)
    annual = annual_breakup_from_surveys(surveys)
    return surveys, annual
