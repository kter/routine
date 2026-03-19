# Architecture Redesign

## Scope

This document defines a clean-slate application design for this repository under one fixed constraint:

- The AWS composition must remain the same.

That means the redesign must continue to operate with:

- `frontend`: Vite SPA hosted on S3 + CloudFront
- `backend`: FastAPI running in a single AWS Lambda behind API Gateway HTTP API
- `auth`: Cognito User Pool + App Client
- `database`: Aurora DSQL
- `evidence storage`: S3
- `tenant provisioning`: Cognito PostConfirmation Lambda

This is not a proposal to introduce new runtime infrastructure. It is a proposal to make the application architecture coherent within the existing infrastructure seams.

## Design Scorecard

Current score: `68/100`

Main reasons:

- The infrastructure shape is coherent for the product.
- The application shape is only partially coherent.
- There is meaningful separation of concerns, but the boundaries are not strict enough.
- The persistence layer and migration layer drift from each other.
- The frontend has feature folders, but not a strong application model.

## Constraints

The following constraints are treated as fixed:

- One backend Lambda handles the API.
- One PostConfirmation Lambda provisions tenants.
- API Gateway uses a single Lambda proxy entrypoint.
- Cognito remains the authentication source.
- `custom:tenant_id` remains the tenant context carried in the token.
- Aurora DSQL remains the primary database.
- Evidence upload remains S3 presigned URL based.
- The frontend remains a client-rendered SPA.

Implications:

- We should design a modular monolith, not pretend we have service boundaries we do not actually operate.
- We should optimize for clear internal boundaries, low Lambda cold-start overhead, and predictable database access.
- We should avoid internal architecture that is more fragmented than the deployment topology.

## Diagnosis

### What Is Working

- The domain itself is understandable: task definitions, steps, execution runs, evidence, tenant provisioning.
- Backend code already attempts layered separation.
- Tenant-aware behavior exists end-to-end.
- Frontend is already organized by feature at the filesystem level.
- Tests exist across unit, integration, and E2E layers.

### What Is Not Working

#### Backend

- `application/` and `usecases/` both exist as business-logic layers.
- Tenant context is passed repeatedly even after it is already established in request scope.
- Dashboard read logic uses in-memory composition where a dedicated read path is more appropriate.
- ORM models, migrations, and DSQL compatibility decisions are not aligned.
- Tenant provisioning sits outside the main architectural shape.

#### Frontend

- Pages still own too much orchestration.
- API DTOs and feature UI types are coupled.
- The custom fetch abstraction is useful but stops short of a real application data model.
- Some UI vocabulary mixes task-definition state and execution-run state.

#### Cross-Cutting

- The system has the shape of a single product, but the codebase still reflects partially competing architecture styles.
- Important invariants live in code convention rather than one explicit boundary.

## Target Architecture

The target architecture is:

- one deployable backend
- one deployable frontend
- strict module boundaries inside each deployable
- explicit application layer
- explicit request context
- separated command and read paths where needed

In short:

- **Deploy as a monolith**
- **Design as bounded modules**

## Architectural Principles

1. One runtime boundary, many internal modules.
2. Request context is established once and reused everywhere.
3. Domain types are not HTTP DTOs.
4. Read models and write models may differ when the use case requires it.
5. Database schema, ORM mapping, and migrations must agree exactly.
6. Tenant isolation is a first-class invariant, not repeated glue code.
7. Frontend pages should be route entries, not orchestration centers.
8. Infrastructure constraints should shape the design, not be ignored by it.

## Backend Target Shape

### Module Boundaries

Reorganize backend code by business context first, then by layer.

Suggested structure:

```text
backend/src/routineops/
  app/
    bootstrap.py
    request_context.py
    errors.py
  contexts/
    tasks/
      domain/
      application/
      infrastructure/
      presentation/
    executions/
      domain/
      application/
      infrastructure/
      presentation/
    dashboard/
      application/
      infrastructure/
      presentation/
    tenants/
      domain/
      application/
      infrastructure/
      presentation/
  shared/
    auth/
    db/
    storage/
    observability/
    config/
  main.py
```

Rationale:

- Business modules become the primary unit of change.
- Each module owns its own public API internally.
- Shared code is limited to genuinely cross-cutting concerns.

### Application Layer

Collapse `application/` and `usecases/` into one explicit application layer.

Responsibilities:

- execute use cases
- enforce business workflows
- coordinate repositories and gateways
- translate domain/application errors

Examples:

- `CreateTask`
- `UpdateTask`
- `StartExecution`
- `CompleteExecutionStep`
- `GetDashboard`
- `ProvisionTenantAfterSignup`

Rule:

- route handlers call application services
- application services call repositories/gateways
- repositories do not contain workflow logic

Transition rule:

- `routineops.application.*` is the canonical import surface
- `routineops.usecases.*` has been removed
- new code must use `routineops.application.*` directly

### Request Context

Introduce one request-scoped object:

```text
RequestContext
  tenant_id
  user_sub
  auth_claims
  request_id
```

This context is created once from Cognito JWT verification and injected into application services.

Consequences:

- do not pass `tenant_id` through every method after the request boundary
- repositories are initialized with request context or tenant scope
- audit fields such as `created_by` use the same source consistently

### Domain Model

Keep the current core domain, because it matches the product:

- `Task`
- `TaskStep`
- `Execution`
- `ExecutionStep`
- `Tenant`

But strengthen the boundaries:

- task definition state stays separate from execution state
- execution step snapshot remains explicit
- validation belongs in domain or application, not split randomly

### Persistence Design

The persistence layer needs simplification and alignment.

Rules:

- one canonical schema definition
- one canonical ORM mapping
- migrations must match that mapping exactly
- DSQL compatibility choices are deliberate and documented, not incidental

Specific direction:

- avoid partial “pretend relational” modeling if DSQL support requires compromises
- if a field is stored as textified JSON, model it consistently as such
- if relationships and foreign keys are supported and relied on, use them consistently

The worst current state is mixed assumptions. That should be eliminated first.

### Read Side

The dashboard should become a dedicated read module.

Recommended shape:

- `dashboard.application.get_dashboard`
- `dashboard.infrastructure.dashboard_query_repository`

The read path should:

- query only the data required
- limit time windows intentionally
- avoid loading all executions into memory for reconciliation

This is the place where denormalized SQL or specialized query objects are justified.

### Tenant Provisioning

Tenant provisioning should be a normal business module, not a side-path.

Target flow:

1. Cognito PostConfirmation handler receives event
2. handler maps event into application input
3. `tenants.application.provision_tenant_after_signup` runs
4. infrastructure adapters perform:
   - tenant record creation
   - any bootstrap records
   - Cognito attribute writeback

This preserves the existing AWS trigger while making the code fit the same architecture as the API.

### API Layer

The API layer should be thin and stable.

Responsibilities:

- parse HTTP input
- resolve request context
- call application services
- map results to response DTOs

Non-responsibilities:

- business workflow
- tenant ownership checks beyond request-context resolution
- persistence concerns

## Frontend Target Shape

### Module Boundaries

Organize frontend by domain/application/UI boundaries, not only by feature folder naming.

Suggested structure:

```text
frontend/src/
  app/
    router/
    providers/
  domains/
    tasks/
      model/
      api/
      queries/
      commands/
      ui/
    executions/
      model/
      api/
      queries/
      commands/
      ui/
    dashboard/
      model/
      api/
      queries/
      ui/
    auth/
      model/
      api/
      queries/
      commands/
      ui/
  shared/
    http/
    forms/
    ui/
    monitoring/
    utils/
  pages/
```

This is still feature-oriented, but separates:

- domain model
- transport/API mapping
- data access
- view components

### Data Layer

Replace the custom ad hoc fetch state pattern with a query/cache layer.

Expected behavior:

- request deduplication
- stale/refetch control
- mutation invalidation
- better retry handling
- fewer page-level loading spinners wired by hand

The current `useApiResource` abstraction is reasonable for a small app, but it is already acting like a lightweight query library without offering the operational advantages of one.

### API Contracts

Separate three kinds of types:

- API DTOs
- domain entities/view models
- form input models

Rules:

- transport code does not import UI feature types
- conversion happens in one place
- pages and components consume domain/view models, not raw DTOs

### Pages

Pages should become thin route entries.

Responsibilities:

- assemble page-level sections
- read route params
- invoke domain queries/commands

Non-responsibilities:

- hand-written orchestration across multiple unrelated APIs
- transport-level mapping
- embedded workflow rules

For example:

- “start execution from dashboard” should be an execution command exposed by the executions module, not a page directly calling an unrelated API file.

### Auth

Keep Cognito + Amplify because the AWS design requires it, but isolate it better.

Auth module responsibilities:

- session restoration
- token retrieval
- user profile extraction
- sign-in/sign-up/sign-out flows
- route protection helpers

Registration and login should follow the same module conventions instead of splitting flow logic between page code and feature code.

### UX Vocabulary

Normalize the product language:

- task = recurring definition/template
- execution = one run instance
- step = definition step or execution step, depending on context
- status labels must reflect the correct lifecycle

This sounds cosmetic, but it drives better type design and cleaner component reuse.

## Shared Cross-Cutting Design

### Errors

Standardize application errors across backend and frontend.

Backend:

- domain/application exceptions map to stable HTTP problem shapes

Frontend:

- transport errors map to user-facing messages in one place

### Observability

Keep Sentry because it already fits the AWS topology.

Improve by:

- adding request context metadata
- tagging tenant-safe identifiers carefully
- separating expected business errors from unexpected system failures

### Configuration

Settings should stay centralized but become more explicit by runtime role.

Recommended groups:

- API runtime settings
- PostConfirmation runtime settings
- shared AWS integration settings
- local/test overrides

## What Should Be Preserved

These decisions are worth keeping:

- FastAPI + Mangum
- Cognito JWT-based auth
- `custom:tenant_id` as tenant context carrier
- Aurora DSQL with IAM auth
- SQLite fallback for tests
- S3 presigned evidence upload flow
- SPA hosted on CloudFront/S3
- Terraform workspace based environment separation

These are aligned with the existing AWS footprint and do not need to be discarded.

## What Should Be Rebuilt

These areas should not be carried forward unchanged:

- split business layers with overlapping meaning
- repeated tenant propagation
- mixed persistence assumptions
- page-heavy frontend orchestration
- DTO/domain/view-model coupling
- dashboard in-memory reconciliation path

## Migration Plan

This redesign should be implemented incrementally, not as a flag day rewrite.

### Phase 1: Establish Stable Foundations

- introduce `RequestContext`
- standardize backend error mapping
- define target backend module conventions
- define target frontend module conventions
- document schema/ORM alignment rules

Outcome:

- new code has a destination architecture
- old code can coexist while migration begins

### Phase 2: Fix Persistence Alignment

- reconcile Alembic schema with ORM definitions
- remove accidental type drift around JSON/TEXT handling
- document DSQL-specific constraints explicitly

Outcome:

- persistence becomes trustworthy
- future refactors stop compounding mismatch

### Phase 3: Extract Tenant Module

- create explicit tenants application service
- move PostConfirmation flow to that service
- align tenant bootstrap logic with repository/gateway conventions

Outcome:

- provisioning stops being special-case infrastructure code

### Phase 4: Refactor Task and Execution Modules

- move task logic into `contexts/tasks`
- move execution logic into `contexts/executions`
- stop passing tenant id through every use-case method
- simplify repositories around request-scoped tenant enforcement

Outcome:

- core product flows gain coherent boundaries

Exit criteria:

- API wiring imports application services directly
- repositories and ports import from `application/*`
- unit tests for business workflows live under `tests/unit/application/`
- no `usecases/` compatibility package remains in the backend tree

### Phase 5: Rebuild Dashboard Read Path

- replace in-memory dashboard composition
- create dashboard-specific query repository
- add focused tests around schedule/execution reconciliation

Outcome:

- dashboard scales better and becomes easier to reason about

### Phase 6: Frontend Data Layer Upgrade

- introduce query/cache library
- migrate dashboard, tasks, executions flows
- move API mapping out of page code

Outcome:

- frontend state flow becomes predictable
- loading/error/invalidation behavior is standardized

### Phase 7: Frontend Module Cleanup

- separate DTOs from domain/view models
- make pages thin
- normalize task vs execution UI vocabulary
- consolidate auth flows

Outcome:

- frontend structure matches product structure

### Phase 8: Compatibility Cleanup

- remove the `routineops.usecases` compatibility facade
- remove legacy `build_*_usecases` and `get_*_usecases` aliases
- update residual documentation and examples to reference `application/*`

Outcome:

- one canonical vocabulary remains in code and docs

## Priority Order

If engineering capacity is limited, the recommended order is:

1. persistence alignment
2. request context and tenant simplification
3. dashboard read path
4. frontend data layer
5. frontend module cleanup

Reason:

- persistence and tenant correctness are risk reducers
- dashboard is the main architectural hotspot
- frontend cleanup pays off more after backend seams are stable

## Acceptance Criteria

The redesign should be considered successful when:

- each backend feature belongs to one bounded module
- there is one unambiguous application layer
- request context is created once per request and reused
- migrations and ORM mappings no longer drift
- dashboard reads use a dedicated read path
- tenant provisioning follows the same architectural shape as the rest of the backend
- frontend pages are thin route entries
- frontend transport, domain, and view types are separated
- the system still deploys on the exact same AWS composition

## Final Recommendation

Do not redesign this system as if it were a distributed system.

Redesign it as a **strict modular monolith** that accepts the truth of its infrastructure:

- one backend deployment
- one frontend deployment
- clear internal boundaries
- explicit tenant context
- clean persistence model
- dedicated read paths where needed

That design is both more honest and more maintainable than the current halfway state.
