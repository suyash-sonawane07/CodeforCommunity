# tests/contract

Guards the binding frontend↔backend contract: every PRD §10.1 endpoint must exist
in the generated OpenAPI spec, and `docs/api/openapi/openapi.json` must match the
app (contract-drift guard). Run: `make test-contract`.
