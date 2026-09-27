# tests/smoke — live-stack checks

Run **while the stack is up** (either workflow):

```bash
make smoke                       # skips what isn't running
BACKEND_URL=http://localhost:8000 FRONTEND_URL=http://localhost:3000 make smoke
```

`tests/integration/` currently re-exports the runnable DB integration checks
(`backend/tests/integration/test_database.py` runs them when Postgres is up);
E2E browser checks arrive with Member A's Phase 2 screens.
