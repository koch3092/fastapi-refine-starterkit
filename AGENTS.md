# Agent Guide

Loaded automatically by AGENTS.md-aware agents at session start. Read before acting.

## TL;DR

- Stack: FastAPI + SQLModel + PostgreSQL backend; Vite + React 19 + Refine + shadcn/ui + Tailwind CSS frontend; npm and `uv`.
- This repository is a business-agnostic starter kit. Keep auth, users, items, assets, Refine data access, migrations, tests, and docs reusable.
- Backend list APIs follow `@refinedev/simple-rest`; use `fastapi-refine` helpers instead of one-off query parsing.
- S3-compatible object storage is enabled by default through the `assets` resource. Local Docker uses MinIO.
- Verify before claiming done: run the relevant backend lint/tests, regenerate the client if API schemas change, and run frontend lint/build for frontend changes.
- Never hand-edit generated files, lockfiles, migrations already in history, or secrets.

## Repository Map

```
.
├── backend/                    # FastAPI service (Python 3.10+, uv)
│   ├── app/
│   │   ├── api/routes/         # HTTP routes
│   │   ├── api/deps/           # Dependency injection and Refine query helpers
│   │   ├── services/           # Business and CRUD logic
│   │   ├── core/               # config, db, security
│   │   ├── alembic/versions/   # Alembic migrations
│   │   └── main.py             # ASGI entrypoint
│   ├── tests/
│   └── scripts/                # lint.sh, test.sh, format.sh, prestart.sh
├── frontend/                   # Vite + React + Refine admin console
│   ├── src/pages/              # CRUD pages grouped by resource
│   ├── src/providers/          # auth, data, constants
│   └── package.json
├── docs/contracts/             # Cross-layer API contracts
├── scripts/
└── AGENTS.md
```

## Do Not Hand-Edit

| Path | Reason |
| --- | --- |
| `backend/app/alembic/versions/*` already committed | Migration history is append-only. Add a new migration instead. |
| `frontend/openapi.json` | Generated OpenAPI snapshot. Regenerate from backend. |
| `frontend/src/client/**` | Generated OpenAPI types/schemas. Regenerate, never edit by hand. |
| `backend/uv.lock`, `frontend/package-lock.json` | Update through `uv lock` / `npm install`, never by hand. |
| `.env`, `.env.*` except `.env.example` | Secrets. Do not read, log, echo, or commit. |
| `node_modules/`, `.venv/`, `.ruff_cache/`, `.pytest_cache/`, `htmlcov/` | Build/cache artifacts. |
| `.github/workflows/**` | CI config. Touch only when the task explicitly calls for it. |

## Commands

Run from the repo root unless noted.

| Task | Command |
| --- | --- |
| Full local stack | `docker compose watch` |
| Install frontend deps | `npm install --prefix frontend` |
| Frontend dev server | `npm run dev --prefix frontend` |
| Frontend build | `npm run build --prefix frontend` |
| Backend deps | `cd backend && uv sync` |
| Backend dev server | `cd backend && uv run fastapi dev app/main.py` |
| Backend lint | `cd backend && uv run bash scripts/lint.sh` |
| Backend tests | `cd backend && uv run bash scripts/test.sh` |
| Generate frontend OpenAPI types | `bash scripts/generate-client.sh` |

## Backend Conventions

- API layer handles HTTP concerns only: routing, dependencies, request/response models, and response headers.
- Service layer owns business rules and database access. Do not scatter SQLModel session logic through routes or utils.
- `fastapi_refine` query configuration belongs in `app/api/**`; services receive normalized conditions, ordering, offsets, and limits.
- List endpoints used by Refine must support `_start`, `_end`, `_sort`, `_order`, filters, and return `x-total-count`.
- Runtime API errors are normalized by `fastapi-refine` through `configure_refine(app)`.
- Common OpenAPI error responses are declared on the top-level API router with `refine_error_responses(...)`.
- The `assets` resource owns S3/MinIO file metadata. Browser uploads use presigned URLs; regular users only see/delete their own assets, while superusers can see/delete all assets.
- Python code is typed, ruff-formatted, and mypy-strict. Add concise Google-style docstrings for new or touched functions.

## Frontend Conventions

- Refine resources are declared in `frontend/src/App.tsx`; CRUD pages live under `frontend/src/pages/<resource>/`.
- The global data provider is `@refinedev/simple-rest` in `frontend/src/providers/data.ts`.
- Resource names map directly to backend paths under `API_URL`; keep backend route paths and Refine resource names aligned.
- API base URL comes from `VITE_API_URL` via `frontend/src/providers/constants.ts`.
- OpenAPI generation is type/schema only: `frontend/src/client/index.ts`, `frontend/src/client/schemas.gen.ts`, and `frontend/src/client/types.gen.ts`. Do not generate or use runtime API clients such as `client.gen.ts`, `services.gen.ts`, or `sdk.gen.ts`.

## Verification Gate

Run the subset that matches what changed:

- Edited `backend/**`: `cd backend && uv run bash scripts/lint.sh`
- Edited backend API or models: run affected route tests, and regenerate any generated client if present
- Edited `frontend/**`: `npm run build --prefix frontend`
- Changed dependencies: update lockfiles through the package manager
- Changed Refine/simple-rest behavior: add or update a route/provider test where practical

If a command fails, report the exact command and the failure. Do not weaken tests to make them pass.
