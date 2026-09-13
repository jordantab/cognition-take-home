.PHONY: install seed api web dev lint typecheck build check

PY := api/.venv/bin/python

install:
	python3 -m venv api/.venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r api/requirements.txt
	cd web && npm install

seed:
	cd api && .venv/bin/python -m app.seed.seed

api:
	cd api && .venv/bin/uvicorn app.main:app --reload --port 8000

web:
	cd web && npm run dev

# Run the API and the web app together.
dev:
	$(MAKE) -j2 api web

lint:
	cd api && .venv/bin/ruff check . && .venv/bin/ruff format --check .
	cd web && npm run lint

typecheck:
	cd web && npm run typecheck

build:
	cd web && npm run build

check: lint build
