# Internal Tools Platform — Prototype Plan

**Audience:** VP Eng, Series C fintech (~60 engineers), deciding Power Apps vs. Devin Cloud for internal tools.

**Thesis to demonstrate:** internal tools built with Devin in a real codebase *compound*. The first app pays for the platform; the next ones are mostly configuration and composition. Power Apps apps are individually cheap but do not accumulate into shared, testable, owned engineering assets.

---

## 1. What we build

**Scope: the AML Investigation Queue only.** It is built on a generic case platform, so a second app later is a case-type config file plus a couple of evidence components rather than a rewrite.

Candidate follow-on apps, if time permits (not in scope now):

| App | Why it would be cheap | Expected new code |
|-----|-----------------------|-------------------|
| **KYC / Onboarding Review** | Same case lifecycle; new evidence = documents + watchlist hits | Low |
| **Refunds & Disputes** | Adds a metrics surface + approval thresholds by role | Low–Medium |
| **Vendor Access Requests** | Essentially a config entry | Very low |

The compounding argument is still made explicitly, just structurally rather than by shipping app #2: the README and `/platform` page show exactly which blocks are app-agnostic and what a second app would cost.

## 2. Tech stack (as proposed, confirmed)

- **Frontend:** Next.js (App Router) + TypeScript, Tailwind, shadcn/ui
- **Tables/charts:** shadcn table primitives wrapped in a declaration-driven `WorkQueue`, Recharts
- **Backend:** Python FastAPI, Pydantic v2, SQLModel/SQLAlchemy
- **DB:** SQLite, deterministic Faker seed script (`make seed`)
- **Types:** FastAPI OpenAPI → `openapi-typescript` generated client, so the frontend never hand-writes API types
- **Identity:** mocked — a user switcher in the top bar; role carried in a header the API trusts
- **No deployment.** `make dev` runs both servers locally.

## 3. Repo shape

```
/web            Next.js app
  /app
    /[caseType]             generic queue + case detail routes (serve /aml)
    /platform               "Building blocks" gallery  <- demo money shot
  /components
    /ui         shadcn primitives (generated)
    /kit        THE PLATFORM LAYER (reusable, app-agnostic)
    /aml        app-specific evidence components only
  /lib          generated API client, auth/role hooks, formatters
/api            FastAPI service
  /core         case engine: models, state machine, audit, RBAC
  /casetypes    one config module per app (states, fields, reason codes, SLAs)
  /seed         Faker seeders
AGENTS.md       conventions + "use these blocks before writing new ones"
```

Single Next app rather than a `packages/*` monorepo: same reuse story, far less tooling surface to explain in a demo. Easy to promote `components/kit` into a package later, and I'll note that path in the README.

## 4. The platform layer (what gets reused)

**UI blocks (`components/kit`)**
- `WorkQueue` — server-driven table: filters, sort, pagination, bulk actions, saved views
- `FilterBar` + `SavedViews`
- `CaseShell` — three-pane case detail: header summary, tabbed evidence, right rail
- `DecisionPanel` — approve / reject / escalate with reason codes, required notes, four-eyes enforcement
- `AuditTimeline` — renders the append-only event log
- `CommentThread` — notes with @mentions of mock users
- `EntityCard` / `EvidenceCard` / `DocumentViewer` / `AttachmentList`
- `StatusBadge`, `RiskScoreBadge`, `SLAClock`, `MetricTiles`, `TrendChart`
- `RoleGate` + `usePermissions`, `ExportCsvButton`

**Backend core (`api/core`)**
- One generic case model: `cases`, `case_events` (audit), `comments`, `attachments`, `decisions`
- Entity graph: `customers`, `accounts`, `transactions`, `merchants`, `watchlist_hits`, `documents`
- `users` + `roles` + permission matrix
- A small **state machine engine**: each case type declares states, transitions, who may perform them, and what a transition requires (note, reason code, second approver)
- Generic endpoints: `GET /cases?type=`, `GET /cases/{id}`, `POST /cases/{id}/transition`, `/comments`, `/saved-views`, `/metrics`

Adding a second app = a new `casetypes/<name>.py` config + one or two evidence components. That is the demo.

## 5. Roles & mock identity

Switcher personas: **Analyst**, **Senior Analyst**, **Compliance Manager**, **Ops Agent**, **Admin**. Switching persona live in the demo visibly changes available actions, queue scope, and approval limits — a concrete "this is real RBAC, not a form" moment.

## 6. Seeded data

Deterministic seed (fixed RNG): ~150 customers, ~5k transactions, ~60 AML alerts (structuring, rapid-movement, sanctions-adjacent patterns), ~200 audit events, 6 users. The seed generates realistic clusters so the alerts actually look investigable.

## 7. Proving the compounding claim

A `/platform` page inside the app, generated from a build-time script, showing:
- the component gallery (every block, live, with the apps that consume it)
- which blocks are app-agnostic vs. AML-specific, and the share of the AML app that is already reusable
- the concrete cost of app #2: the files a KYC queue would add, versus the files it inherits

If we build a second app, this page gains a real new-vs-reused LOC comparison — the artifact the VP screenshots for their own exec review.

## 8. Why this beats the Power Apps comparison (talking points, in the README)

- Code is owned, diffable, reviewable, testable — 60 engineers can work in it
- Reuse is real and measurable; Power Apps components don't accumulate the same way across makers
- No per-user/per-app licensing cliff; no premium connector tax for custom data
- Devin gets faster as the repo grows: `AGENTS.md`, knowledge notes, and existing blocks are context for the next app
- Escape hatch: anything custom (risk scoring, data joins, integrations) is just Python

## 9. Build sequence

1. Scaffold repo, `make dev`, seed script, mock auth, shadcn baseline, `AGENTS.md`
2. Case engine + `components/kit` platform layer
3. AML queue + case detail, decisioning, audit trail
4. `/platform` gallery; README narrative
5. If time permits: a second app (KYC first choice) to make the compounding visible in a diff

## 10. Open questions

1. **Demo format** — live click-through, or should I also produce a recorded walkthrough?
2. **Second app** — if time permits, KYC is my default pick; a tool this company has actually complained about would land better.
3. **Metrics page** — worth the build, or keep the reuse numbers in the README only?
