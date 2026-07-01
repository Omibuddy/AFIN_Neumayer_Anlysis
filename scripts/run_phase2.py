#!/usr/bin/env python3
"""Orchestrate revised Phase 2: download, sensitivity, spatial stats, Antarctic."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: str, *args: str) -> None:
    cmd = [sys.executable, str(ROOT / script), *args]
    print(f"\n{'=' * 64}\n>>> {' '.join(cmd)}\n{'=' * 64}")
    subprocess.run(cmd, check=True)


def main() -> None:
    steps = [
        ("scripts/download_gridded.py", "CDRv6 gridded download"),
        ("scripts/sensitivity_analysis.py", "Figs 2 + 3"),
        ("scripts/spatial_exploration.py", "Pearson-r heat map + composite (Fig 5)"),
        ("scripts/plot_antarctic_calendar.py", "Fig 4 Antarctic calendar"),
    ]
    print("Phase 2 spatial exploration pipeline")
    for script, label in steps:
        print(f"\n--- {label} ---")
        run(script)
    print("\nPhase 2 pipeline complete.")


if __name__ == "__main__":
    main()
