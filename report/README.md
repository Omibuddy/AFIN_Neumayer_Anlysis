# One-page LaTeX report

## Files

| File | Description |
|------|-------------|
| `one_pager.tex` | Auto-generated from `results/summary.json` |
| `one_pager.pdf` | Compile locally (not in repo by default) |

## Compile

Requires [MacTeX](https://www.tug.org/mactex/) or TeX Live:

```bash
# From project root (after run_analysis.py)
cd report
pdflatex -interaction=nonstopmode one_pager.tex
pdflatex -interaction=nonstopmode one_pager.tex
```

Or: `make pdf` from project root.

The figure path is `../results/figures/doy_minimum_trend.png` relative to this folder.

## Before submitting

1. Set `project.author` in `config.yaml`
2. Run `python scripts/run_analysis.py`
3. Compile PDF and submit `one_pager.pdf`
