# Publishing on GitHub

## Initial setup

```bash
cd /path/to/project
git init
git add .
git commit -m "Initial commit: Arctic SIA minimum timing analysis (April 2026)"
```

Create a new repository on GitHub (empty, no README), then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/arctic-sia-minimum-timing.git
git branch -M main
git push -u origin main
```

## Before you push

1. **Set your name** in `config.yaml`:
   ```yaml
   project:
     author: "Omkar Someshwar Kondhalkar"  # example
   ```
2. Re-run analysis so LaTeX matches:
   ```bash
   python scripts/run_analysis.py
   ```
3. **Optional:** Compile PDF locally and commit `report/one_pager.pdf` (or use GitHub Actions — see below).

## Recommended repository settings

| Setting | Recommendation |
|---------|----------------|
| License | MIT for code (already in `LICENSE`) |
| Topics | `sea-ice`, `climate`, `arctic`, `python`, `university-of-hamburg` |
| About | Short description + link to figure in README |

## Keeping the project updated

When new satellite months are available (e.g. after summer 2026):

```bash
python scripts/download_data.py
# Edit config.yaml if you extend data_cutoff beyond 2026-04-30
python scripts/run_analysis.py
git add results/ docs/RESULTS.md report/one_pager.tex data/raw/
git commit -m "Update analysis through YYYY-MM"
git push
```

Auto-updated files after each `run_analysis.py`:

- `results/summary.json`
- `results/figures/doy_minimum_trend.png`
- `results/tables/*.csv`
- `docs/RESULTS.md`
- `report/one_pager.tex`

## Data in the repository

Raw files in `data/raw/` total ~3 MB — acceptable for GitHub. To keep the repo smaller:

1. Uncomment `# data/raw/` in `.gitignore`
2. Document that users must run `python scripts/download_data.py`
3. Commit only `results/` and code

## Optional: GitHub Actions CI

Create `.github/workflows/analysis.yml`:

```yaml
name: analysis
on: [push, workflow_dispatch]
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: python scripts/download_data.py
      - run: python scripts/run_analysis.py
```

## README badge (optional)

After pushing, your README figure will render from `results/figures/doy_minimum_trend.png` on the default branch.
