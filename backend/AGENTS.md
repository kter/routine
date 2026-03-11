# AGENTS.md

## Scope

Instructions for work under `backend/`.

Inherit the repository-level guidance from the parent `AGENTS.md`. When backend-specific guidance conflicts with parent guidance, this file takes precedence.

## Command Policy

- Prefer root `make` targets for routine workflows.
- Common entry points: `make dev-backend`, `make test-unit`, `make test-integration`, `make lint-backend`, `make db-migrate ENV=dev`.
- Use direct `uv` commands only when working on backend internals that are not exposed via the root `Makefile`.

## Environment

Common `.env` keys:
- `AWS_REGION`
- `DB_CLUSTER_ENDPOINT`
- `DB_NAME`
- `COGNITO_CLIENT_ID`
- `COGNITO_JWKS_URL`
- `EVIDENCE_BUCKET_NAME`
- `CORS_ORIGINS`

Testing-specific overrides:
- `DB_TYPE=sqlite`
- `SQLITE_PATH`
- `TEST_MODE=true`

## Backend Notes

- The API is built with FastAPI and served locally with `uvicorn`.
- Production runtime is AWS Lambda via `Mangum`.
- The default database path is Aurora DSQL; tests use SQLite in-memory mode.
- Authentication verifies Cognito JWTs and extracts `custom:tenant_id` plus `sub` from the token.
- Database schema changes should go through Alembic migrations.
- Backend code targets Pydantic v2 and Python 3.12.
