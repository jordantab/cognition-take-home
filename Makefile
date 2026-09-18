.PHONY: install seed api web dev lint lint-api lint-web typecheck build test e2e schema schema-check check

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

lint: lint-api lint-web

lint-api:
	cd api && .venv/bin/ruff check . && .venv/bin/ruff format --check .

lint-web:
	cd web && npm run lint

typecheck:
	cd web && npm run typecheck

build:
	cd web && npm run build

test:
	cd api && .venv/bin/python -m pytest

# Browser golden path against a freshly seeded fixture.
# Needs `cd web && npx playwright install --with-deps chromium` once.
e2e: seed
	cd web && npx playwright test

# Regenerate the OpenAPI document and the frontend types derived from it.
schema:
	cd api && .venv/bin/python -c 'import json; from app.main import app; print(json.dumps(app.openapi(), indent=2))' > ../web/lib/api/openapi.json
	cd web && npx openapi-typescript lib/api/openapi.json -o lib/api/schema.d.ts

# Fails when the committed frontend types no longer match the API.
schema-check: schema
	git diff --exit-code -- web/lib/api/openapi.json web/lib/api/schema.d.ts

check: lint typecheck test schema-check build
