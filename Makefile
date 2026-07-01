.PHONY: setup data analyze docs pdf clean all phase2

PYTHON ?= python3

setup:
	$(PYTHON) -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -r requirements.txt

data:
	$(PYTHON) scripts/download_data.py

analyze:
	$(PYTHON) scripts/run_analysis.py

phase2:
	.venv/bin/python scripts/run_phase2.py

docs:
	$(PYTHON) scripts/update_docs.py
	$(PYTHON) scripts/generate_latex.py

pdf:
	cd report && pdflatex -interaction=nonstopmode one_pager.tex
	cd report && pdflatex -interaction=nonstopmode one_pager.tex

report:
	cd report && pdflatex -interaction=nonstopmode full_report.tex
	cd report && pdflatex -interaction=nonstopmode full_report.tex
	cd report && pdflatex -interaction=nonstopmode slides.tex

clean:
	rm -rf report/*.aux report/*.log report/*.out report/*.synctex.gz
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

all: analyze pdf
