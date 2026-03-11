# AGENTS.md

## Scope

Instructions for the entire repository.

More specific instructions may exist in nested `AGENTS.md` files. When instructions conflict, the nearer file takes precedence.

## Overview

This repository is a RoutineOps tracker built on a split frontend, backend, and infrastructure stack.
- `frontend/`: Vite + React + TypeScript SPA
- `backend/`: FastAPI application packaged for AWS Lambda
- `infra/`: Terraform infrastructure
- `tests/`: unit, integration, and E2E tests

## Shared Rules

- The root `Makefile` is the canonical entry point for project workflows.
- Use the tool versions defined in `mise.toml`.
- Add or update tests for every new feature and bug fix.
- Prefer adding reusable workflow shortcuts to the root `Makefile` instead of introducing one-off command sequences.
- Run cross-stack workflows, deployment, and Terraform operations from the repository root.
- Prefer root `make` targets over direct `aws`, `terraform apply`, or ad hoc deployment commands for routine workflows.

## Common Commands

```bash
make dev
make test
make lint
make deploy ENV=prd
make tf-plan ENV=dev
```
