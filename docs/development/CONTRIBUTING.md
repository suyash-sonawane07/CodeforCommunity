# Contributing

Small-team rules that keep 3-way parallel work mergeable (PRD §18.2).

## Ownership (hard boundaries)

| Directory | Owner |
|---|---|
| `frontend/` | Member A |
| `backend/` | Member B |
| `ai/`, `data/` | Member C |
| `deploy/`, CI | Member B |
| `docs/api/API_CONTRACT.md`, `docs/api/openapi/openapi.json`, `backend/app/schemas/`, `frontend/types/` | **shared** — contract PR + 1 reviewer |

Details: `docs/team/MEMBER_{A,B,C}.md`.

## Branching & PRs

See [`WORKFLOW.md`](WORKFLOW.md). Summary: never push `main`; work on
`feature/member-x/...`; every PR needs 1 teammate review and must reference PRD FR-/S-IDs.

## Contracts before implementation

1. Need a changed/added endpoint or field? Open a **contract PR** first
   (`API_CONTRACT.md` + regenerated `openapi.json` + Pydantic/TS types together).
2. Merge it, then implement against it. No consumer may code against an unmerged contract.

## Definition of done (per task)

- [ ] Code on a feature branch, PR open, PRD IDs referenced
- [ ] Contract-compliant (schemas match OpenAPI)
- [ ] At least a smoke test covers the change; `make test` and `make lint` pass
- [ ] Demoable on the running stack
- [ ] If data is synthetic → labelled `SYNTHETIC` (FR-057); if state-changing → audit-log TODO (FR-062)

## Scaffold invariants (don't break)

- Business endpoints return `501 NOT_IMPLEMENTED` until implemented — never fake success payloads.
- No hardcoded URLs in the frontend — only `NEXT_PUBLIC_API_BASE_URL` via `lib/api.ts`.
- No hardcoded priority weights, thresholds, distances, or confidence values (§26 of the brief) — future config goes through settings/config objects.
- Original citizen text/audio is immutable once written (FR-004); location never fabricated (FR-021/033).
- Real secrets never enter the repo.

## Style

- Python: `ruff` (lint + format), line length 100 — `make format`.
- TS/JS: `eslint` + `prettier`, strict TS — `npm run format` in `frontend/`.
- Commits: small, imperative subject, body explains *why*.
