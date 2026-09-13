# Northwind Internal Case Platform — AML Investigation Queue

A working prototype of an internal tool built the way an engineering org would actually own it: a real Next.js + FastAPI codebase, a generic case-management core, and a library of reusable building blocks. The first app shipped on it is an **AML investigation queue** with queue triage, evidence review, role-based decisioning, four-eyes SAR approval, and a full audit trail.

Everything runs locally against seeded SQLite data. No deployment, no external services.

## Why it is built this way

The point of the prototype is not the AML app in isolation — it is that the AML app left behind a platform:

- **The queue, filters, saved views, case shell, decision panel, audit timeline, comments, assignment, CSV export, metrics and charts are app-agnostic.** They render from declarations the API returns.
- **An app is a declaration, not a codebase.** `api/app/casetypes/aml.py` declares AML's states, transitions, permissions, SLA, queue columns, filters, saved views, summary fields and evidence tabs. The generic engine does the rest.
- **The only AML-specific frontend code is four evidence components** (`web/components/aml/`) — flagged transactions, customer profile, screening hits, related alerts.

Visit `/platform` in the running app: it lists every block, marks shared vs. app-specific, counts the lines of each, and shows the AML case-type declaration in full. A second app (KYC review, refunds, vendor access) is a new `casetypes/*.py` plus its evidence components; it inherits the routes, queue, workflow UI, RBAC and audit trail unchanged.

Compared with a low-code tool: this is diffable, reviewable, testable, and owned by the 60 engineers who already work in the repo — and the reuse compounds across apps instead of being re-drawn per maker.

## Run it

Requires Python 3.11+, Node 20+.

```bash
make install   # python venv + npm install
make seed      # deterministic SQLite seed
make dev       # API on :8000, web on :3000
```

Then open http://localhost:3000 (redirects to `/aml`). API docs at http://localhost:8000/docs.

Other targets: `make lint`, `make typecheck`, `make build`, `make api`, `make web`.

## Mock identity and roles

Identity is mocked: the web app stores the selected persona in a cookie and sends it as `X-User-Id`; the API resolves the user and enforces that user's permissions. Switch persona from the sidebar — the UI changes immediately.

| Persona | Role | Can do |
|---|---|---|
| Amelia Ortiz | Analyst | Claim, investigate, request info, close no-action, recommend SAR |
| Dev Raman | Analyst | Same as above |
| Priya Nair | Senior Analyst | Analyst actions plus reassignment |
| Marcus Webb | Compliance Manager | Approve and file SARs, reject recommendations |
| Sofia Lindqvist | Ops Agent | Read-only across the queue, can comment |
| Rae Patel | Admin | Everything |

**Four-eyes approval:** `file_sar` requires the `case:approve` permission *and* an actor different from the analyst who recommended it. Recommend a SAR as Amelia, switch to Marcus, and the approval unlocks; as Amelia it stays locked with the reason shown.

## Architecture

```
api/
  app/core/       case engine: models, workflow config, RBAC, service layer, mock identity
  app/casetypes/  one declaration module per app (aml.py)
  app/routes/     generic REST endpoints over any case type
  app/seed/       deterministic Faker seed
web/
  app/[caseType]/           generic queue route  (serves /aml today)
  app/[caseType]/[caseId]/  generic case detail route
  app/platform/             building-block gallery
  components/kit/           the reusable platform layer
  components/aml/           AML-only evidence components
  lib/                      API client, generated OpenAPI types, formatters
```

Endpoints are generic over case type:

```
GET  /api/case-types                      declarations for every registered app
GET  /api/case-types/{type}/cases         filter, search, sort, paginate
GET  /api/case-types/{type}/metrics       tiles, trend, breakdowns
GET  /api/cases/{id}                      case + evidence + available transitions
POST /api/cases/{id}/transition           workflow move, permission + note checked
POST /api/cases/{id}/comments
POST /api/cases/{id}/assignee
```

Frontend types are generated from the API's OpenAPI schema (`web/lib/api/schema.d.ts`), so the contract cannot silently drift:

```bash
cd web && npx openapi-typescript http://localhost:8000/openapi.json -o lib/api/schema.d.ts
```

## Seeded data

Fixed RNG seed (`api/app/settings.py`): 6 users, 140 customers, 220 accounts, ~4.6k transactions, 64 AML alerts across structuring / rapid-movement / sanctions-adjacent typologies, plus watchlist hits, comments and audit history. Re-running `make seed` reproduces the same dataset.

See [PLAN.md](PLAN.md) for the full design rationale and the roadmap for follow-on apps.
