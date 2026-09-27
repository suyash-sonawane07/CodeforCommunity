# ADR-001 — Modular monolith

- **Status:** Accepted · **Date:** 2026-09-27 · **Owner:** Member B

## Context
3-person hackathon team, demo-scale load; PRD §9.3/§12 explicitly reject microservices
for the MVP. Multiple deployables would add contract, deployment and debugging overhead
with no benefit at this scale.

## Decision
One FastAPI process (modular monolith). Internal layering:
`api/routes → services → repositories → db`. The `ai/` directory is a library imported
into the same deployment, not a separate service. No network hops inside the backend.

## Reason
Minimal DevOps burden for 3 people; transactional integrity across cluster/evidence
writes; fast iteration during a hackathon; PRD-mandated.

## Alternatives
Microservices (rejected — PRD §12 "explicitly rejected — avoid overengineering");
serverless functions (rejected — stateful DB access + AI pipeline fits a monolith better).

## Consequences
- Scaling beyond demo would require extraction — boundaries (`services/` pure logic, `repositories/` data access) are drawn so extraction is cheap.
- One deploy unit; a crash affects everything (acceptable at demo scale).
- Contract between frontend/backend is still strictly HTTP/JSON (OpenAPI).
