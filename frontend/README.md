# Frontend — CivicPulse

**Owner: Member A (Frontend/UX)** — see `docs/team/MEMBER_A.md`.

**SCAFFOLD ONLY** — pages render as placeholders; no business logic implemented.
All screens (S-01…S-15) exist as routes with TODO(PRD S-xx) comments.

## Stack

Next.js 14 (App Router) · React 18 · TypeScript strict · Tailwind CSS 3 · Jest + Testing Library

## Commands

```bash
npm install        # first time
npm run dev        # dev server on ${FRONTEND_PORT:-3000}
npm run test       # Jest unit tests
npm run lint       # ESLint (next/core-web-vitals)
npm run typecheck  # tsc --noEmit
npm run build      # production build
npm run format     # Prettier write (format:check to verify)
```

## Layout

| Path                  | Purpose                                                       |
| --------------------- | ------------------------------------------------------------- |
| `app/`                | Route pages for S-01…S-15 (one page per PRD screen)           |
| `components/ui/`      | Shared primitives (Button, Card, ErrorState, ScaffoldNotice…) |
| `components/layouts/` | AppShell sidebar + PageContainer                              |
| `lib/api.ts`          | **Single API client** — only place that calls the backend     |
| `lib/config.ts`       | Reads `NEXT_PUBLIC_API_BASE_URL` (never hardcode URLs)        |
| `types/api.ts`        | TS mirror of backend schemas (keep in sync with contract)     |
| `hooks/useApi.ts`     | Minimal fetch hook (loading/error/data)                       |
| `tests/`              | Jest + Testing Library tests                                  |

## Rules for Member A

- Screens are placeholders until the matching backend endpoint returns real data.
- Handle `ApiError` with `code === "NOT_IMPLEMENTED"` via `<ErrorState error={...} />`.
- Map tiles: dynamically import Leaflet (`next/dynamic`, `ssr: false`).
- Keep `types/api.ts` aligned with `docs/api/openapi/openapi.json` (contract tests guard drift).
