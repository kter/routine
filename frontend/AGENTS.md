# AGENTS.md

## Scope

Instructions for work under `frontend/`.

Inherit the repository-level guidance from the parent `AGENTS.md`. When frontend-specific guidance conflicts with parent guidance, this file takes precedence.

## Command Policy

- Prefer root `make` targets for routine workflows.
- Common entry points: `make dev-frontend`, `make lint-frontend`, `make build-frontend ENV=dev`, `make test-e2e`.
- Use direct `npm` or `playwright` commands only for frontend-local debugging that is not exposed via the root `Makefile`.

## Environment

Common frontend env keys:
- `VITE_API_BASE_URL`
- `VITE_COGNITO_USER_POOL_ID`
- `VITE_COGNITO_CLIENT_ID`
- `VITE_COGNITO_REGION`

Required for E2E:
- `E2E_TEST_USER_EMAIL`
- `E2E_TEST_USER_PASSWORD`

## Frontend Notes

- Frontend is a Vite + React + TypeScript SPA.
- Routing is handled with `react-router-dom`.
- Authentication is handled with Amplify and Cognito.
- Styling uses Tailwind CSS.
