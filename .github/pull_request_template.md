## Summary

<!-- One or two sentences: what does this PR change? -->

## PRD traceability

<!-- Reference requirement IDs — required per docs/development/WORKFLOW.md -->

- PRD screens: S-__
- PRD requirements: FR-___
- PRD API: §10.1 endpoint(s): ___
- PRD entities: §9.1 table(s): ___

## Checklist

- [ ] Small, focused commit range (reviewable in <15 min)
- [ ] No hardcoded URLs — API base comes from `NEXT_PUBLIC_API_BASE_URL` / `DATABASE_URL`
- [ ] Backend changes: `docs/api/openapi/openapi.json` re-exported if routes changed
      (`make openapi-export`); contract tests pass
- [ ] Frontend changes: `types/api.ts` still matches the contract
- [ ] No real secrets committed (`.env` is gitignored)
- [ ] Tests added/updated; `make test` passes locally
- [ ] Honest scope: no feature claimed as working unless it is (PRD §21.7)
