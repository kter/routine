.PHONY: dev dev-frontend dev-backend \
        test test-frontend test-unit test-integration test-e2e smoke-deploy \
        lint lint-frontend lint-backend lint-backend-fast typecheck-frontend \
        fmt fmt-terraform fmt-backend fmt-frontend \
        format-check-backend format-check-frontend \
        claude-post-edit agent-stop-unit-tests claude-stop-unit-tests \
        build build-frontend build-lambda \
        tf-bootstrap tf-init tf-plan tf-apply tf-destroy \
        deploy deploy-frontend \
        db-migrate db-seed \
        install-hooks clean help

# ──────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────
ENV ?= dev
BACKEND_DIR := backend
FRONTEND_DIR := frontend
INFRA_DIR := infra
DB_DIR := db
TESTS_DIR := tests

LAMBDA_ZIP := lambda.zip

# ──────────────────────────────────────────────────────────────────────
# Local Development
# ──────────────────────────────────────────────────────────────────────

## dev: Start frontend + backend locally (requires tmux or runs in background)
dev:
	@echo "Starting frontend and backend..."
	@$(MAKE) -j2 dev-frontend dev-backend

## dev-frontend: Start Vite dev server
dev-frontend:
	cd $(FRONTEND_DIR) && npm run dev

## dev-backend: Start FastAPI uvicorn server
dev-backend:
	cd $(BACKEND_DIR) && uv run uvicorn src.routineops.main:app --reload --host 0.0.0.0 --port 8000

# ──────────────────────────────────────────────────────────────────────
# Testing
# ──────────────────────────────────────────────────────────────────────

## test: Run frontend + backend tests
test: test-frontend test-unit test-integration

## test-frontend: Run frontend unit tests
test-frontend:
	cd $(FRONTEND_DIR) && npm run test

## test-unit: Run unit tests only
test-unit:
	cd $(BACKEND_DIR) && uv run pytest $(CURDIR)/$(TESTS_DIR)/unit -v --tb=short

## test-integration: Run integration tests only
test-integration:
	cd $(BACKEND_DIR) && uv run pytest $(CURDIR)/$(TESTS_DIR)/integration -v --tb=short

## test-e2e: Run E2E tests against dev environment (requires E2E_TEST_USER_EMAIL and E2E_TEST_USER_PASSWORD)
test-e2e:
	@echo "Running E2E tests against dev environment..."
	@export E2E_TEST_USER_EMAIL="$(shell grep E2E_TEST_USER_EMAIL $(FRONTEND_DIR)/.env.local 2>/dev/null | cut -d= -f2-)" && \
	export E2E_TEST_USER_PASSWORD="$(shell grep E2E_TEST_USER_PASSWORD $(FRONTEND_DIR)/.env.local 2>/dev/null | cut -d= -f2-)" && \
	npx playwright test --config=playwright.config.ts

## smoke-deploy: Run authenticated dashboard smoke test against the deployed frontend (ENV=dev|prd)
smoke-deploy:
	@echo "Running post-deploy smoke test for ENV=$(ENV)..."
	@terraform -chdir=$(INFRA_DIR) workspace select $(ENV) >/dev/null && \
	export PLAYWRIGHT_BASE_URL=$$(terraform -chdir=$(INFRA_DIR) output -raw frontend_url 2>/dev/null) && \
	export E2E_TEST_USER_EMAIL="$(shell grep E2E_TEST_USER_EMAIL $(FRONTEND_DIR)/.env.local 2>/dev/null | cut -d= -f2-)" && \
	export E2E_TEST_USER_PASSWORD="$(shell grep E2E_TEST_USER_PASSWORD $(FRONTEND_DIR)/.env.local 2>/dev/null | cut -d= -f2-)" && \
	test -n "$$PLAYWRIGHT_BASE_URL" && \
	test -n "$$E2E_TEST_USER_EMAIL" && \
	test -n "$$E2E_TEST_USER_PASSWORD" && \
	npx playwright test --config=playwright.config.ts tests/e2e/deploy-smoke.spec.ts --project=chromium

# ──────────────────────────────────────────────────────────────────────
# Lint
# ──────────────────────────────────────────────────────────────────────

## lint: Run all linters
lint: lint-frontend lint-backend

## lint-frontend: Run ESLint on frontend
lint-frontend:
	cd $(FRONTEND_DIR) && npm run lint

## lint-backend: Run ruff + mypy on backend
lint-backend:
	cd $(BACKEND_DIR) && uv run ruff check src/
	cd $(BACKEND_DIR) && uv run mypy src/

## lint-backend-fast: Run fast backend lint checks for hooks
lint-backend-fast:
	cd $(BACKEND_DIR) && uv run ruff check src/ $(CURDIR)/$(TESTS_DIR)/

## typecheck-frontend: Run TypeScript type-check on frontend
typecheck-frontend:
	cd $(FRONTEND_DIR) && npm run type-check

# ──────────────────────────────────────────────────────────────────────
# Format
# ──────────────────────────────────────────────────────────────────────

## fmt: Format all code (terraform + backend + frontend)
fmt: fmt-terraform fmt-backend fmt-frontend

## fmt-terraform: Format Terraform files
fmt-terraform:
	terraform -chdir=$(INFRA_DIR) fmt -recursive
	terraform -chdir=$(INFRA_DIR)/bootstrap fmt -recursive

## fmt-backend: Format Python backend with ruff
fmt-backend:
	cd $(BACKEND_DIR) && uv run ruff format src/
	cd $(BACKEND_DIR) && uv run ruff format $(CURDIR)/$(TESTS_DIR)/

## fmt-frontend: Format frontend with prettier
fmt-frontend:
	cd $(FRONTEND_DIR) && npm run format

## format-check-backend: Check Python formatting without modifying files
format-check-backend:
	cd $(BACKEND_DIR) && uv run ruff format --check src/ $(CURDIR)/$(TESTS_DIR)/

## format-check-frontend: Check frontend formatting without modifying files
format-check-frontend:
	cd $(FRONTEND_DIR) && npm run format:check

## claude-post-edit: Run fast format/lint fixes for a single file edited by Claude Code (FILE=path/to/file)
claude-post-edit:
	@test -n "$(FILE)" || (echo "FILE is required" >&2; exit 1)
	@file="$(FILE)"; \
	case "$$file" in \
		frontend/*.ts|frontend/*.tsx) \
			rel_path="$${file#frontend/}"; \
			cd $(FRONTEND_DIR) && npx eslint --fix "$$rel_path" && npx prettier --write "$$rel_path" ;; \
		frontend/*.css) \
			rel_path="$${file#frontend/}"; \
			cd $(FRONTEND_DIR) && npx prettier --write "$$rel_path" ;; \
		backend/*.py|tests/*.py|.claude/*.py|.claude/*/*.py|.claude/*/*/*.py) \
			abs_path="$(CURDIR)/$$file"; \
			cd $(BACKEND_DIR) && uv run ruff check --fix "$$abs_path" && uv run ruff format "$$abs_path" ;; \
		infra/*.tf|infra/*.tfvars|infra/bootstrap/*.tf|infra/bootstrap/*.tfvars) \
			terraform fmt "$(CURDIR)/$$file" >/dev/null ;; \
		*) \
			exit 0 ;; \
	esac

## agent-stop-unit-tests: Run unit tests from agent Stop hooks
agent-stop-unit-tests:
	@$(MAKE) test-unit

## claude-stop-unit-tests: Backward-compatible alias for the shared Stop-hook unit tests target
claude-stop-unit-tests:
	@$(MAKE) agent-stop-unit-tests

# ──────────────────────────────────────────────────────────────────────
# Build
# ──────────────────────────────────────────────────────────────────────

## build: Build frontend + Lambda zip
build: build-frontend build-lambda

## build-frontend: Build React SPA using Terraform outputs for the selected ENV when available
build-frontend:
	@echo "Building frontend for ENV=$(ENV)..."
	@if terraform -chdir=$(INFRA_DIR) workspace select $(ENV) >/dev/null 2>&1 && \
		terraform -chdir=$(INFRA_DIR) output -raw api_url >/dev/null 2>&1; then \
		cd $(FRONTEND_DIR) && \
		VITE_API_BASE_URL="$$(terraform -chdir=$(CURDIR)/$(INFRA_DIR) output -raw api_url)" \
		VITE_COGNITO_USER_POOL_ID="$$(terraform -chdir=$(CURDIR)/$(INFRA_DIR) output -raw cognito_user_pool_id)" \
		VITE_COGNITO_CLIENT_ID="$$(terraform -chdir=$(CURDIR)/$(INFRA_DIR) output -raw cognito_client_id)" \
		npm run build; \
	else \
		echo "Terraform outputs for ENV=$(ENV) are unavailable; using frontend/.env defaults."; \
		cd $(FRONTEND_DIR) && npm run build; \
	fi

## build-lambda: Package backend as Lambda zip
build-lambda:
	@echo "Building Lambda package..."
	rm -rf /tmp/lambda-build
	cd $(BACKEND_DIR) && uv export --no-dev --no-hashes --no-emit-project -o /tmp/lambda-requirements.txt
	pip install -r /tmp/lambda-requirements.txt -t /tmp/lambda-build --quiet
	cp -r $(BACKEND_DIR)/src/routineops /tmp/lambda-build/
	cd /tmp/lambda-build && zip -r $(CURDIR)/$(LAMBDA_ZIP) . -x "*.pyc" -x "__pycache__/*" -x "*.dist-info/*"
	@echo "Lambda zip created: $(LAMBDA_ZIP)"

# ──────────────────────────────────────────────────────────────────────
# Terraform
# ──────────────────────────────────────────────────────────────────────

## tf-bootstrap: Create remote state S3 bucket (run once, ENV selects AWS profile)
tf-bootstrap:
	@echo "Bootstrapping Terraform remote state for ENV=$(ENV)..."
	terraform -chdir=$(INFRA_DIR)/bootstrap init
	terraform -chdir=$(INFRA_DIR)/bootstrap apply -auto-approve -var="aws_profile=$(ENV)"

## tf-init: Initialize Terraform and select workspace (ENV=dev|prd)
tf-init:
	@echo "Initializing Terraform for ENV=$(ENV)..."
	terraform -chdir=$(INFRA_DIR) init
	terraform -chdir=$(INFRA_DIR) workspace select $(ENV) || \
		terraform -chdir=$(INFRA_DIR) workspace new $(ENV)

## tf-plan: Plan Terraform changes (ENV=dev|prd)
tf-plan:
	@echo "Planning Terraform for ENV=$(ENV)..."
	terraform -chdir=$(INFRA_DIR) workspace select $(ENV)
	terraform -chdir=$(INFRA_DIR) plan -out=$(ENV).tfplan

## tf-apply: Apply Terraform changes (ENV=dev|prd)
tf-apply:
	@echo "Applying Terraform for ENV=$(ENV)..."
	terraform -chdir=$(INFRA_DIR) workspace select $(ENV)
	terraform -chdir=$(INFRA_DIR) apply $(ENV).tfplan

## tf-destroy: Destroy Terraform resources (ENV=dev|prd) - requires confirmation
tf-destroy:
	@echo "WARNING: This will destroy all resources in ENV=$(ENV)!"
	@read -p "Type the environment name to confirm: " confirm; \
		if [ "$$confirm" = "$(ENV)" ]; then \
			terraform -chdir=$(INFRA_DIR) workspace select $(ENV); \
			terraform -chdir=$(INFRA_DIR) destroy; \
		else \
			echo "Aborted."; \
			exit 1; \
		fi

# ──────────────────────────────────────────────────────────────────────
# Deploy
# ──────────────────────────────────────────────────────────────────────

## deploy: Full deploy (lambda build → tf-init → tf-plan → tf-apply → frontend build → S3 sync → CF cache invalidation)
deploy:
	@echo "Deploying to ENV=$(ENV)..."
	$(MAKE) build-lambda && \
	$(MAKE) tf-init ENV=$(ENV) && \
	$(MAKE) tf-plan ENV=$(ENV) && \
	$(MAKE) tf-apply ENV=$(ENV) && \
	$(MAKE) db-migrate ENV=$(ENV) && \
	$(MAKE) build-frontend ENV=$(ENV) && \
	$(MAKE) deploy-frontend ENV=$(ENV) && \
	if [ "$(ENV)" = "dev" ]; then $(MAKE) smoke-deploy ENV=$(ENV); fi

## deploy-frontend: Sync frontend build to S3 and invalidate CloudFront cache
deploy-frontend:
	@echo "Deploying frontend to S3 for ENV=$(ENV)..."
	@terraform -chdir=$(INFRA_DIR) workspace select $(ENV) >/dev/null
	$(eval BUCKET := $(shell terraform -chdir=$(INFRA_DIR) output -raw frontend_bucket_name 2>/dev/null))
	$(eval CF_ID  := $(shell terraform -chdir=$(INFRA_DIR) output -raw cloudfront_distribution_id 2>/dev/null))
	aws s3 sync $(FRONTEND_DIR)/dist s3://$(BUCKET) --delete --profile $(ENV)
	aws cloudfront create-invalidation --distribution-id $(CF_ID) --paths "/*" --profile $(ENV)

# ──────────────────────────────────────────────────────────────────────
# Database
# ──────────────────────────────────────────────────────────────────────

## db-migrate: Apply DDL schema + indexes (ENV=dev|prd)
db-migrate:
	@echo "Running DB migrations for ENV=$(ENV)..."
	@cd $(BACKEND_DIR) && AWS_PROFILE=$(ENV) ENV=$(ENV) uv run alembic upgrade head

## db-seed: Insert development seed data (ENV=dev only)
db-seed:
	@if [ "$(ENV)" != "dev" ]; then echo "db-seed is only for dev environment"; exit 1; fi
	@echo "Seeding database for ENV=$(ENV)..."
	AWS_PROFILE=$(ENV) psql "$${DB_URL}" -f $(DB_DIR)/seeds/001_dev_seed.sql

# ──────────────────────────────────────────────────────────────────────
# Git Hooks
# ──────────────────────────────────────────────────────────────────────

## install-hooks: Install git hooks via lefthook
install-hooks:
	mise exec -- lefthook install
	@echo "Git hooks installed via lefthook."

# ──────────────────────────────────────────────────────────────────────
# Clean
# ──────────────────────────────────────────────────────────────────────

## clean: Remove build artifacts
clean:
	rm -rf $(FRONTEND_DIR)/dist $(FRONTEND_DIR)/node_modules/.cache
	rm -rf $(BACKEND_DIR)/.venv $(BACKEND_DIR)/__pycache__
	rm -f $(LAMBDA_ZIP)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# ──────────────────────────────────────────────────────────────────────
# Help
# ──────────────────────────────────────────────────────────────────────

## help: Show this help message
help:
	@echo "RoutineOps Tracker - Available Make targets:"
	@echo ""
	@grep -E '^## ' Makefile | sed 's/## /  /' | column -t -s ':'
