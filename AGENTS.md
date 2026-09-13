# Working in this repo

This is a case-management platform with one app on it (AML). The value of the repo is the platform, so the default answer to "where does this code go?" is **the shared layer, made generic** — not the app folder.

## Before writing UI, check the kit

`web/components/kit/` already has: `AppShell`, `PersonaSwitcher`, `PageHeader`, `WorkQueue`, `FilterBar`, `MetricTiles`, `TrendChart`, `BreakdownBars`, `CaseShell`, `SummaryList`, `EvidenceTabs`, `DecisionPanel`, `AuditTimeline`, `CommentThread`, `AssigneePicker`, `StatusBadge`/`PriorityBadge`/`TagBadge`, `RiskScore`, `SlaClock`, `UserChip`, `RoleGate`/`can`, `ExportCsvButton`, `EmptyState`, `FactGrid`, `useQueueParams`.

Reuse or extend one of those before adding a component. Anything that would be useful to a second app belongs in `kit/` and must not import from `components/aml/` or reference AML concepts.

`web/components/ui/` is generated shadcn — add primitives with `npx shadcn@latest add <name>`, don't hand-write them.

## Adding a new app (KYC, refunds, vendor access, …)

1. Write `api/app/casetypes/<name>.py`: states, transitions (permission, required note/reason code, four-eyes via `distinct_actor_from`), queue columns, filters, saved views, summary fields, evidence tabs, SLA. Import the module in `api/app/main.py` (and in the seed script) so it registers itself.
2. Seed data for it in `api/app/seed/`.
3. Add its evidence components under `web/components/<name>/` and register them in `web/lib/registry.ts` under the case-type key, matching the component names used in the declaration.

That is the whole app. Routes (`/<caseType>`, `/<caseType>/<caseId>`), queue, filters, workflow UI, RBAC, audit trail and metrics are already generic. **If a new app requires changes to `api/app/core/` or `web/components/kit/`, make the change generic and configuration-driven rather than branching on case type.**

## Conventions

- No hard-coded statuses, transitions, columns or labels in the frontend: they come from `GET /api/case-types/*` and are rendered from `State`/`Column`/`Filter`/`SummaryField` declarations.
- All permission decisions are enforced server-side in `api/app/core/service.py`. Frontend gating is a UX affordance only, via `can()`/`RoleGate`.
- Every state change, assignment and comment writes a `CaseEvent`; the audit log is append-only.
- Frontend types come from `web/lib/api/schema.d.ts`, generated from OpenAPI. Never hand-write API types; regenerate after changing response models (see README).
- Data fetching happens in server components through `web/lib/api.ts`; mutations go through server actions in `web/app/actions.ts`, which `revalidatePath` afterwards.
- Seed data must stay deterministic — use the module's RNG seeded from `api/app/settings.py`, never `random` or `datetime.now()` directly at import time.
- Python: `ruff check` + `ruff format` clean. TypeScript: `npm run lint`, `npm run typecheck`, `npm run build` clean.
- `web/AGENTS.md` applies to frontend work: this is Next.js 16 (App Router, Turbopack, async `cookies()`/`params`/`searchParams`). Read `web/node_modules/next/dist/docs/` before assuming an API.

## Checks

```bash
make lint        # ruff + eslint
make typecheck   # tsc --noEmit
make build       # next build
make seed        # rebuild the SQLite fixture
```

When adding a block to `components/kit/`, also add it to `web/lib/blocks.ts` so the `/platform` gallery stays accurate.
