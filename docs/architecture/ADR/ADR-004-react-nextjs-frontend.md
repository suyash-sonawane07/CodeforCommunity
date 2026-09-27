# ADR-004 — React / Next.js frontend

- **Status:** Accepted · **Date:** 2026-09-27 · **Owner:** Member A

## Context
Need a data-dense planner dashboard (S-05…S-11) *and* simple, low-end-friendly citizen
screens (S-01…S-03), built fast by one person (PRD §8, §12). Mobile behaviour and
multilingual UI chrome are required.

## Decision
Next.js (App Router) + TypeScript **strict** + Tailwind CSS. Leaflet + OpenStreetMap
planned for map screens (no API key, per PRD §12). All backend access flows through one
API client in `frontend/lib/api.ts` reading `NEXT_PUBLIC_API_BASE_URL` — no hardcoded
URLs anywhere else.

## Reason
Team likely has prior React exposure (PRD §12); Tailwind keeps the design system small;
App Router file conventions map 1:1 onto the 15-screen inventory; TS strict + generated
types later (from OpenAPI) prevent contract drift for a solo frontend dev.

## Alternatives
Vite + plain React (viable; rejected — App Router's file-based routing and layout
nesting fit the screen inventory better); plain HTML/JS (rejected in PRD — too slow for
dashboard interactivity); component libraries (rejected — heavier than the 3-person
design-system need).

## Consequences
- Node 20+ required for dev; CI typecheck/lint/test run on every PR.
- Frontend is mostly client-side placeholder pages now; data fetching will be introduced per-screen in Phase 2 against the contract.
- Leaflet needs dynamic import (no SSR) when implemented — noted in map component TODOs.
