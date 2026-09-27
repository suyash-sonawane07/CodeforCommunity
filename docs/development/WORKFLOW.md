# Git Workflow

Branching model from PRD §18.2, adapted to the 3-member scaffold.

```
main                  (always demoable; protected; no direct pushes)
 └─ phase-1           (integration branch for Phase 1)
     ├─ feature/member-a/frontend-shell
     ├─ feature/member-b/backend-foundation
     └─ feature/member-c/ai-foundation
```

Later phases: repeat with `phase-2`, `phase-3`.

## Rules

1. `main` must always remain demoable.
2. **No direct pushes to `main`** (or `phase-N`). Everything via PR.
3. Every feature gets its own branch: `feature/member-<x>/<topic>`.
4. **Pull request required** — one teammate reviews every PR.
5. PR descriptions must reference the relevant **PRD IDs** (FR-xxx / S-xx / journey #).
6. Never merge unrelated changes together — one topic per PR.
7. Keep commits small and descriptive (`feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`).
8. **Shared contracts first:** OpenAPI / `API_CONTRACT.md` / shared types change in a
   contract PR **before** dependent implementation PRs.
9. End-of-phase = mandatory full-stack integration checkpoint; no one starts the next
   phase's UI/logic against an unmerged contract (PRD R-07).

## Daily commands

```bash
git switch main && git pull
git switch -c feature/member-a/frontend-shell        # example
# ...work in small commits...
git push -u origin feature/member-a/frontend-shell
# open PR against phase-1 (not main) → request review → merge after approval
```

## PR template

`.github/pull_request_template.md` pre-fills: PRD FR IDs, what/why, testing,
screenshots (frontend), breaking changes, contract changes.

## Merge conflicts

- Directory ownership (see CONTRIBUTING) keeps conflicts rare.
- Shared files (`schemas/`, `types/`, `openapi.json`) are the exception — contract PRs only, merge quickly, one at a time.
- Regenerate `docs/api/openapi/openapi.json` after any Pydantic schema change (`make openapi-export`) and commit it in the same PR.
