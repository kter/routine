# AGENTS.md

## Scope

Instructions for work under `infra/`.

Inherit the repository-level guidance from the parent `AGENTS.md`. When infrastructure-specific guidance conflicts with parent guidance, this file takes precedence.

## Command Policy

- Use the root `Makefile` as the canonical entry point.
- Common entry points: `make tf-bootstrap ENV=dev`, `make tf-init ENV=dev`, `make tf-plan ENV=dev`, `make tf-apply ENV=dev`, `make tf-destroy ENV=dev`, `make fmt-terraform`.
- Run Terraform workflows from the repository root.

## Infrastructure Notes

- Use Terraform workspaces for environment separation (`dev`, `prd`).
- Bootstrap state configuration lives in `infra/bootstrap/`.
- The main Terraform root module lives in `infra/`.
- `ENV` is used to select the workspace and corresponding AWS profile.
- `lambda.zip` is built at the repository root and consumed by Terraform-managed Lambda resources.
- Prefer root `make` targets for Terraform and deployment workflows instead of direct routine apply/deploy commands.
