# fastapi-refine-starterkit

A business-agnostic full-stack starter: a FastAPI + SQLModel + PostgreSQL backend and a
React + Refine admin console wired through the `@refinedev/simple-rest` protocol.

The reusable infrastructure is intentionally small: JWT auth, users, items, S3-compatible
assets, Alembic migrations, Refine-compatible list APIs, unified API error envelopes,
Docker Compose, and focused tests. Add project-specific domain models and pages on top.

## What's Included

- **Backend API**: FastAPI, SQLModel, Pydantic v2, PostgreSQL, Alembic
- **Auth**: OAuth2 password login, JWT access tokens, password reset helpers
- **Users and items**: baseline CRUD resources for admin-console scaffolding
- **Assets**: default S3/MinIO-backed file resource with presigned browser uploads
- **Refine integration**: list pagination/sorting/filtering through `fastapi-refine`
- **Unified errors**: runtime and OpenAPI error envelopes from `fastapi-refine`
- **Frontend**: React 19, TypeScript, Vite, Refine, React Router 7, Ant Design
- **OpenAPI types**: generated `frontend/openapi.json` and type/schema artifacts only
- **Tooling**: `uv`, ruff, mypy, pytest, npm, Docker Compose

## Quick Start

```bash
# 1. Configure environment
cp .env.example .env

# 2. Start db + backend + frontend
docker compose watch
```

- Frontend: <http://localhost:5173>
- Backend API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- MinIO API: <http://localhost:9000>
- MinIO Console: <http://localhost:9001>
- MailCatcher: <http://localhost:1080>

The default admin login comes from `FIRST_SUPERUSER` and
`FIRST_SUPERUSER_PASSWORD` in `.env`.

## Local Development

```bash
# Backend
cd backend
uv sync
uv run fastapi dev app/main.py

# Frontend
npm install --prefix frontend
npm run dev --prefix frontend
```

## Common Commands

| Task | Command |
| --- | --- |
| Backend lint + types | `cd backend && uv run bash scripts/lint.sh` |
| Backend tests | `cd backend && uv run bash scripts/test.sh` |
| Frontend build | `npm run build --prefix frontend` |
| Generate OpenAPI types | `bash scripts/generate-client.sh` |
| Full stack | `docker compose watch` |

`scripts/generate-client.sh` regenerates `frontend/openapi.json` and only these
frontend artifacts: `frontend/src/client/index.ts`, `schemas.gen.ts`, and
`types.gen.ts`. The starterkit does not generate or use a runtime TypeScript API client.

## Adding a Resource

1. Add SQLModel models in `backend/app/models.py`.
2. Add service functions under `backend/app/services/`.
3. Add routes under `backend/app/api/routes/` and include them in `backend/app/api/main.py`.
4. For Refine list pages, define `FilterConfig` / `SortConfig` in the API layer and return `x-total-count`.
5. Add frontend pages under `frontend/src/pages/<resource>/` and register the resource in `frontend/src/App.tsx`.
6. Generate and review an Alembic migration for schema changes.
7. If API schemas changed, run `bash scripts/generate-client.sh` and commit the generated artifacts.

## Contracts

- [Refine simple-rest](./docs/contracts/refine-simple-rest.md)
- [OpenAPI error envelope](./docs/openapi-error-envelope-contract.md)
- [Backend query layering](./backend/docs/contracts/refine-query-contract.md)

## Docs

- [Development guide](./development.md)
- [Deployment guide](./deployment.md)
- [Backend notes](./backend/README.md)
- [Frontend notes](./frontend/README.MD)
