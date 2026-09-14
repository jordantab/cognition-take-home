# AML Investigation Queue

## Overview

A prototype internal tool for a financial crime team: a queue of anti-money-laundering alerts that
analysts triage, investigate against seeded evidence, and either close or escalate for a SAR
decision. It is one app — a Next.js frontend, a FastAPI backend, and a seeded SQLite database —
running entirely locally with no external services.

Devin was the primary building tool for this repository. The stack, data model, workflow
configuration, UI components and seed data were built through Devin sessions, with review and
direction from a human.

## What it demonstrates

- A complete internal workflow end to end: queue with search, filters, saved views, sorting,
  paging and CSV export; a case workspace with evidence tabs, comments and an audit history; and
  role-gated decisions enforced on the server.
- Case-management components and patterns that are not specific to AML: the queue, filter bar,
  metric tiles, trend chart, case shell, decision panel, audit timeline, comment thread, assignee
  picker, badges and SLA clock all render from declarations the API returns
  (`api/app/casetypes/aml.py`). Only four components — the AML evidence tabs — know what an AML
  alert is.
- Those shared components are candidates for extraction into an internal-tools kit that other apps
  could depend on. In a production setup each internal app would live in its own repository and
  consume that kit as a package, rather than being added here.
- `/platform` lists the components built in this prototype, marks each as shared or AML-specific
  with its line count, and shows the AML case-type declaration in full. The percentage it reports
  covers only the components in that list, not the whole codebase.

## Architecture

```
api/
  app/core/       case model, workflow declarations, RBAC, service layer, mock identity
  app/casetypes/  the AML declaration: states, transitions, columns, filters, evidence tabs
  app/routes/     REST endpoints (generic over case type)
  app/seed/       deterministic Faker seed
web/
  app/[caseType]/           queue and case-detail routes
  app/platform/             component gallery
  components/kit/           shared case-management components
  components/aml/           AML evidence components
  lib/                      API client and types generated from the OpenAPI schema
```

Identity is mocked: the selected persona is stored in a cookie and sent as an `X-User-Id` header;
the API resolves that user and applies their permissions. Three personas are seeded — Amelia Ortiz
(analyst), Priya Nair (senior analyst) and Marcus Webb (compliance manager).

## Run locally

Requires Python 3.11+ and Node 20+.

```bash
make install
make seed
make dev
```

- Web app: http://localhost:3000 (redirects to `/aml`)
- API documentation: http://localhost:8000/docs

`make seed` rebuilds a fixed dataset: 3 users, 140 customers, 220 accounts, ~4,600 transactions and
64 alerts. The RNG seed is fixed, so re-running it reproduces the same data.

## Demo workflow

1. As Amelia (analyst), open an alert from "My open alerts" and review the flagged transactions,
   customer profile, screening hits and related alerts.
2. Claim and start the review, then either close it with a reason code or recommend a SAR with a
   reason code and rationale.
3. Switch to Marcus (compliance manager) in the sidebar. The recommended alert appears under
   "Awaiting my approval", a view analysts do not see.
4. Approve and file the SAR. Four-eyes is enforced server-side: the analyst who recommended it
   cannot approve it, and the button stays locked with the reason shown.
5. Check the audit history on the case — workflow changes, assignments and comments are all
   recorded.

## Prototype limitations

- This is a prototype, not a production-ready AML or compliance system.
- Authentication is mocked. There is no login, session security or tenancy.
- There is no detection engine. Suspicious patterns are written by the seed script, which also
  generates the summary text for each alert.
- "Approve & file SAR" only advances the demo workflow. It does not submit a regulatory report
  anywhere.
- Audit history covers workflow transitions, assignments and comments only.
- There are no automated tests. Verification is `make lint`, `make typecheck` and `make build`.
- Data lives in a local SQLite file and is replaced whenever the seed is re-run.

See [PLAN.md](PLAN.md) for the original design notes.
