# Member A — Frontend & UX

> Owns the entire user-facing layer end-to-end (PRD §17.1). Primary dependency:
> the frozen FastAPI OpenAPI contract — **never backend internals**.

## Owns

- `frontend/` — all of it: app shell, navigation, layouts, design-system primitives
  (`components/ui/`), all 15 screen routes (S-01…S-15), API client (`lib/api.ts`),
  shared types (`types/api.ts`), frontend tests.
- Screen states per PRD §8.1: loading / empty / error / populated / mobile behaviour.

## Must NOT casually modify

- `backend/`, `ai/`, `data/`, `deploy/` — anything outside `frontend/` goes through a PR
  reviewed by its owner.
- `frontend/types/api.ts` is a **shared contract mirror** of the OpenAPI spec — propose
  changes in a contract PR, don't silently reshape shared types.

## Dependencies

- **From Member B:** OpenAPI spec (`docs/api/openapi/openapi.json`) + `API_CONTRACT.md`.
  Build against these while endpoints still return 501 — the schemas are already real.
- **From Member C:** none directly (synthetic-data `SYNTHETIC` labels come from the API
  payloads; flag wording needs to Member B/C via contract PRs).

## Phase mapping (PRD §17)

| Phase | Member A focus |
|---|---|
| 1 | Shell polish, S-01–S-03 citizen flow against stubbed API, wireframes for S-05+ |
| 2 | S-06 map, S-07/S-08 cluster + evidence, S-09 gap view, S-10 equity toggle — wired to real (synthetic) API data |
| 3 | S-11 simulator UI, S-12/S-13 review screens, S-14 outcome view, S-15 settings |

## Screen inventory (PRD §8.1) → routes

| Screen | Route (file) | Status |
|---|---|---|
| S-01 Citizen Landing / Submit | `app/citizen/page.tsx` | shell ✅ |
| S-02 Voice Review | `app/citizen/voice-review/page.tsx` | shell ✅ |
| S-03 Submission Confirmation | `app/citizen/confirmation/page.tsx` | shell ✅ |
| S-04 Admin Login | `app/admin/page.tsx` | shell ✅ |
| S-05 Command Dashboard | `app/admin/dashboard/page.tsx` | shell ✅ |
| S-06 Demand Intelligence Map | `app/map/page.tsx` | shell ✅ |
| S-07 Cluster Detail | `app/clusters/[id]/page.tsx` | shell ✅ |
| S-08 Evidence Panel | `app/clusters/[id]/evidence/page.tsx` | shell ✅ |
| S-09 Infrastructure Gap View | `app/clusters/[id]/gap/page.tsx` | shell ✅ |
| S-10 Equity Comparison | `app/clusters/equity/page.tsx` | shell ✅ |
| S-11 Policy Simulator | `app/simulator/page.tsx` | shell ✅ |
| S-12 Human Review Queue | `app/review/page.tsx` | shell ✅ |
| S-13 Review & Audit Detail | `app/review/[id]/page.tsx` | shell ✅ |
| S-14 Outcome Measurement | `app/outcome/page.tsx` | shell ✅ |
| S-15 Dataset & Settings | `app/datasets/page.tsx` | shell ✅ |

## Commands

```bash
make frontend          # dev server :3000
cd frontend && npm test        # jest
cd frontend && npm run lint && npm run format:check
```

## First tasks (suggested)

1. Wire S-01/S-02/S-03 into a real citizen flow against the 501-stubbed `POST /requests`
   (intake form + consent checkbox + confirmation screen showing the reference code shape).
2. Replace `PagePlaceholder` usage on S-05 with a real dashboard layout fed by
   `GET /clusters` (it will render the error state until Member B implements it — that's correct behaviour).
3. Design-tokens pass on `components/ui/` (spacing/typography) before screens multiply.
