PYTHON ?= python3
TOUR ?= ambos
START_YEAR ?= 2000
END_YEAR ?= 2025

.PHONY: sync-relevante sync-relevante-dry-run sync-bio-historico sync-bio-historico-dry-run test lint check format

test:
	pytest --cov=src --cov=api --cov-report=term-missing

lint:
	ruff check .
	mypy . --ignore-missing-imports

check: lint test

format:
	ruff format .

sync-relevante:
	$(PYTHON) scripts/sync_master_real_data.py --tour $(TOUR) --start-year $(START_YEAR) --end-year $(END_YEAR)

sync-relevante-dry-run:
	$(PYTHON) scripts/sync_master_real_data.py --tour $(TOUR) --start-year $(START_YEAR) --end-year $(END_YEAR) --dry-run

sync-bio-historico: sync-relevante

sync-bio-historico-dry-run: sync-relevante-dry-run
