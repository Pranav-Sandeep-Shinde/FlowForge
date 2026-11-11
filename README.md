# FlowForge

> A workflow automation and execution platform built as a hands-on, production-oriented software engineering project.

FlowForge is intended to let users visually define workflows as connected nodes, validate and publish those workflows, execute a specific published version, and monitor execution progress. The project is designed to explore the engineering problems behind workflow orchestration systems: graph validation, immutable workflow versions, asynchronous execution, retries, failure handling, observability, and real-time updates.

This README is also a project-context document for AI coding agents such as Codex. It describes the confirmed project direction, current technology choices, architectural decisions, known repository structure, implementation status, and recommended next steps.

---

## 1. Product vision

FlowForge aims to provide a visual workflow automation platform. A user should eventually be able to build a process such as:

1. Receive a trigger or start an execution manually.
2. Validate input data.
3. Run one or more operations.
4. Evaluate conditions and choose a path.
5. Run independent operations concurrently where appropriate.
6. Retry transient failures or report permanent failures.
7. Inspect the execution history and see which nodes succeeded or failed.

A workflow is represented as a directed graph:

- **Nodes** represent operations, triggers, conditions, or other units of work.
- **Edges** represent dependencies or connections between nodes.
- **Workflow definitions** are editable representations of the graph.
- **Published workflow versions** are immutable snapshots intended for execution.
- **Executions** are individual attempts to run a particular published version.

The product is inspired by the visual workflow-building experience of tools such as n8n and Zapier and by the durable orchestration concepts found in systems such as Temporal. FlowForge is a learning and portfolio project; it is not intended to reproduce every feature of those products.

## 2. Why this project exists

The goal is to build more than a conventional CRUD application. FlowForge provides a practical environment for learning and demonstrating senior-level backend and full-stack engineering concepts, including:

- Domain boundaries and modular application architecture.
- Relational database modeling and integrity constraints.
- API contracts, validation, authentication, and authorization.
- Directed graphs, cycle detection, dependency resolution, and topological ordering.
- Workflow versioning and reproducible execution.
- Asynchronous task processing and message queues.
- Concurrency, retries, timeouts, cancellation, and failure recovery.
- Consistency, idempotency, and duplicate task-delivery handling.
- WebSockets and event-driven updates.
- Structured logging, request correlation, testing, and observability.
- Frontend/backend integration using typed API contracts.

The implementation should be developed incrementally. Each feature should have a clear purpose, a documented contract, and tests. Avoid adding infrastructure or abstractions merely because they might be useful someday.

## 3. Technology stack

### Backend

| Technology | Intended responsibility |
|---|---|
| Python | Backend language |
| Django | Application framework and ORM |
| Django REST Framework (DRF) | HTTP APIs, serializers, API views, permissions, and exception integration |
| PostgreSQL | Persistent relational data; JSON-capable storage for appropriate snapshots/configuration where justified |
| Redis | Celery broker and Django Channels messaging support |
| Celery | Background and asynchronous task execution |
| Django Channels | WebSocket connections and live execution updates |
| SimpleJWT | JWT-based API authentication |
| drf-spectacular | OpenAPI schema and API documentation |
| django-environ | Environment-based configuration |
| uv | Python dependency and environment management |

### Frontend

| Technology | Intended responsibility |
|---|---|
| React | User interface |
| TypeScript | Typed application code and API contracts |
| Visual graph editor library / implementation | Workflow node canvas, edges, and editing interactions; choice should be evaluated when frontend work begins |

### Development and testing

- `pytest` and `pytest-django` for automated tests.
- Ruff, Black, and isort are included in the development tooling configuration.
- Git is used for version control. The project direction has included `main` and `develop` branches; inspect the current repository state before assuming which branch is checked out.

The latest environment/test output supplied by the user showed Python 3.14.0, Django 6.0.7, pytest 9.1.1, and pytest-django 4.12.0. Confirm installed versions from the active environment rather than assuming they have not changed.

## 4. High-level architecture

The intended system has the following major components:

```text
React + TypeScript frontend
        |
        | HTTP API                         WebSocket
        v                                    ^
Django + Django REST Framework              |
        |                                    |
        +-- Identity / Organizations         |
        +-- Workflows                        |
        +-- Execution coordination           |
        +-- Shared API infrastructure        |
        |                                    |
        v                                    |
PostgreSQL                                  Django Channels
        ^                                    ^
        |                                    |
Celery workers <---- Redis -----------------+
        |
        +-- Execute published workflow snapshots
        +-- Persist execution and node state
        +-- Emit execution events / updates
```

This is the target architecture, not a claim that every component is already implemented or connected.

### 4.1 Domain separation

The main conceptual domains are:

- **Identity:** users and authentication.
- **Organizations:** organization ownership and membership; detailed behavior must be confirmed from the existing code before extending it.
- **Workflows:** editable workflow definitions, nodes, edges, validation, versions, and publishing.
- **Executions:** individual runs of a published workflow version, node-level execution state, outputs, errors, and lifecycle transitions.
- **Shared:** cross-cutting application infrastructure such as standard responses, exceptions, request IDs, and logging.

Do not combine workflow editing and workflow execution into one model or one service. They have different lifecycles and responsibilities.

### 4.2 Workflow definition versus execution

This separation is a core design decision:

1. A user edits a workflow definition.
2. The application validates the graph and node configurations.
3. Publishing creates an immutable compiled snapshot associated with a workflow version.
4. Starting an execution selects a specific published version.
5. The execution uses that version's snapshot even if the editable draft changes or a newer version is published later.

An execution must not silently start using a changed draft midway through its lifetime. Pinning an execution to a published version makes the run reproducible and easier to audit and debug.

### 4.3 Normalized editing data plus immutable execution snapshot

The planned persistence approach is hybrid:

- Use relational models for editable workflow data and relationships, such as `Workflow`, `WorkflowNode`, and `WorkflowEdge`.
- On publishing, validate and compile the definition into a versioned immutable snapshot (likely a JSON representation, with exact schema and storage field to be designed).
- Have each execution reference the published version/snapshot it runs.

Do not assume that saving only a large JSON document is the desired editing model. Do not assume that delta-only snapshot storage is required; immutable published snapshots are the important requirement, while storage optimizations can be considered later.

## 5. Planned workflow and execution behavior

### 5.1 Graph validation

The workflow validation layer is expected to check items such as:

- Node identifiers are unique within the workflow.
- Edges reference nodes belonging to the same workflow.
- Node types are registered and supported.
- Node configuration conforms to the node type's schema.
- Required inputs and connections are present.
- Unsupported cycles are rejected for the initial DAG execution model.
- The graph is structurally executable.

Topological ordering is useful for determining dependency order in a DAG. However, the eventual runtime must do more than iterate through a topological list: it must track node states, schedule ready nodes, handle branches and joins, and coordinate failures, retries, timeouts, and cancellation.

The first engine should support a deliberately small, well-tested graph model. Add more advanced control-flow semantics only after the basic execution path works.

### 5.2 Node registry

The planned node registry is a mapping from node type to its definition/implementation. A node definition may eventually provide:

- Stable node type identifier.
- Configuration validation/schema.
- Execution implementation or executor strategy.
- Input/output metadata.
- Frontend palette/display metadata.

The registry should avoid a large `if/elif` chain in the execution engine and provide a clear extension boundary for new node types. Do not overbuild a plugin framework before a few real node types exist.

### 5.3 Execution context and states

The eventual execution runtime will need an execution context that can track information such as:

- Execution ID and pinned workflow version.
- Current execution status.
- Node statuses and dependency progress.
- Node inputs and outputs.
- Workflow variables / shared execution data where required.
- Retry attempts and errors.
- Cancellation and timeout state.

Potential execution states include `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`, and a retry/waiting state if the design requires one. Define allowed transitions explicitly before implementing them; these names are candidates, not a finalized enum contract.

### 5.4 Asynchronous execution and reliability

The intended direction is to use Celery workers with Redis for background execution. The API should create/persist an execution and enqueue work rather than holding an HTTP request open for a long-running workflow.

Future reliability work should address:

- Transient versus permanent failures.
- Retry policies and backoff.
- Timeouts and cancellation.
- Duplicate task delivery and idempotent task handling.
- Database transactions and the boundary between persisting an execution and enqueueing it.
- Recovery after worker/process interruption.
- Checkpointing or resumability if justified by the first implementation.

Do not claim exactly-once task execution. Design for the delivery guarantees of the chosen queue and make operations safe against duplicate attempts where required.

### 5.5 Real-time updates

Django Channels is planned to deliver execution progress to the frontend. Example events may include execution started, node started, node completed, node failed, retry scheduled, and execution completed. The event schema, authorization rules, ordering, and persistence strategy must be designed when this phase begins.

## 6. Shared foundation: current implementation status

The shared foundation has been built before the workflow domain so that future modules can use consistent infrastructure.

### 6.1 Standard API response contract

The response helpers are in `shared/responses/`. The agreed response envelope is:

Success:

```json
{
  "success": true,
  "data": {},
  "meta": {},
  "errors": null
}
```

Error:

```json
{
  "success": false,
  "data": null,
  "meta": {},
  "errors": [
    {
      "code": "NOT_FOUND",
      "message": "Workflow not found"
    }
  ]
}
```

Exact helper signatures and optional-field behavior should be read from the current source files before modifying them.

### 6.2 Exception hierarchy

The base `FlowForgeException` holds a message, an error code, and an HTTP status code. Specialized exceptions fix their semantic code/status and allow callers to customize the message, rather than allowing callers to create inconsistent combinations.

The implemented/tested mappings include:

| Exception | Error code | HTTP status |
|---|---|---:|
| `ValidationError` | `VALIDATION_ERROR` | 400 |
| `AuthenticationError` | `UNAUTHORIZED` | 401 |
| `PermissionDeniedError` | `FORBIDDEN` | 403 |
| `NotFoundError` | `NOT_FOUND` | 404 |
| `ConflictError` | `CONFLICT` | 409 |

The generic error-code enum belongs in shared infrastructure. Domain-specific error codes should be owned by their domain. Python enums should not be extended by subclassing an existing enum; define separate `StrEnum` classes for separate domains.

### 6.3 Global DRF exception handler

A custom DRF exception handler converts `FlowForgeException` instances into the shared error response and delegates other exceptions to DRF's normal `rest_framework.views.exception_handler`.

The handler is configured through the DRF `EXCEPTION_HANDLER` setting. It has unit tests and an integration test that issues an actual request to a temporary exception endpoint.

The temporary exception endpoint exists for infrastructure testing only. Inspect its current location and usage; remove it or move it into an appropriate test-only arrangement once no longer needed. Do not leave debug/test endpoints exposed as permanent product APIs.

### 6.4 Request ID middleware and logging context

The request ID middleware:

- Generates a server-side UUID4 per incoming request.
- Attaches it to `request.request_id`.
- Adds the value to the `X-Request-ID` response header.
- Uses a `ContextVar` to make the ID available to logging code during the request.
- Resets the context using the token in a `finally` block so request context does not leak.

The logging filter attaches the current context value to each log record as `record.request_id`. Outside an active request, the default is `"-"`.

Django's `LOGGING` configuration was added to use a console handler, formatter, and the custom request ID filter. Read the live settings and logging files before changing them.

The user most recently confirmed that the full pytest suite passed with **17 tests** after resolving a Windows Application Control issue that initially blocked the `pytest` executable. On the LOQ, `uv run python -m pytest` worked. Prefer this invocation if the Windows `pytest.exe` launcher is blocked:

```powershell
uv run python -m pytest
```

The 17-test count is the latest user-provided result, not a promise that the current working tree has not changed since then.

## 7. Current repository structure (confirmed portions)

The user provided this output for `modules/workflows`:

```text
modules/workflows/
    admin.py
    apps.py
    models.py
    tests.py
    views.py
    __init__.py
    api/
        serializers.py
        urls.py
        views.py
        __init__.py
    application/
        health_service.py
    constants/
        error_codes.py
        __init__.py
    migrations/
        __init__.py
```

The user provided this output for `modules/organizations`:

```text
modules/organizations/
    admin.py
    apps.py
    models.py
    tests.py
    views.py
    __init__.py
    api/
        serializers.py
        urls.py
        views.py
        __init__.py
    application/
        health_service.py
```

These are confirmed directory listings only. The contents and behavior of these files have not yet been reviewed in the current project-design discussion. In particular, do not assume that the existing `models.py`, API files, or `health_service.py` are empty or complete; inspect them before changing anything.

The user also ran:

```powershell
uv run python manage.py shell -c "from django.conf import settings; print(settings.AUTH_USER_MODEL)"
```

and got:

```text
auth.User
```

Therefore, the current configured user model is Django's default `auth.User`. When defining user foreign keys, use `settings.AUTH_USER_MODEL` rather than hardcoding `auth.User`, so the code remains compatible with a future custom user model. Do not introduce a custom user model without first reviewing migration history and discussing the migration implications.

The project includes `config` settings and API routing, plus `modules` and `shared` packages. Inspect `INSTALLED_APPS`, URL mounting, settings split, and migration state before making changes.

## 8. Immediate next phase: design the Workflow domain

The shared foundation is considered complete based on the latest passing suite. The next task is to begin the actual workflow domain. Do not immediately generate every model or endpoint. First inspect the existing code and agree on the domain model.

### Recommended first actions

1. Inspect the full contents of:
   - `modules/workflows/models.py`
   - `modules/workflows/apps.py`
   - `modules/workflows/admin.py`
   - `modules/workflows/api/serializers.py`
   - `modules/workflows/api/views.py`
   - `modules/workflows/api/urls.py`
   - `modules/workflows/constants/error_codes.py`
   - `modules/organizations/models.py`
   - `modules/organizations/apps.py`
   - `config/settings/base.py` or the actual settings files in use
   - `pyproject.toml`
2. Inspect installed apps, database configuration, URL prefixes, and migration history.
3. Understand the existing organization model before deciding how a workflow is owned and scoped.
4. Propose and discuss the initial workflow entity and its invariants.
5. Implement only the first model and its tests; run migrations and tests before adding the next model.

### Initial domain concepts to evaluate

These are target concepts, not existing confirmed model definitions:

#### Workflow

Likely responsibilities:

- Stable identity and human-readable name/description.
- Organization ownership or workspace scope, based on the actual organizations domain.
- Creator/owner metadata, using the configured user model where appropriate.
- Draft/lifecycle status and timestamps.
- Relationship to workflow nodes, edges, and published versions.

Decisions still to make: exact ownership model, deletion policy, slug/identifier requirements, draft status semantics, uniqueness scope, and whether archived workflows are soft-deleted or represented with a lifecycle status.

#### WorkflowNode

Likely responsibilities:

- Stable node identity within a workflow.
- Node type identifier (for example, `http_request`, `condition`, or `manual_trigger` in future implementations).
- Display name and configuration.
- Canvas position if needed by the frontend editor.
- Relationships to the parent workflow.

Decisions still to make: UUID versus integer primary key (prefer stable IDs if graph references need them), JSON configuration shape, position representation, and validation ownership.

#### WorkflowEdge

Likely responsibilities:

- A directed connection from one node to another.
- Source and target node references.
- Optional port/handle identifiers if branching or multiple outputs require them.
- Optional edge metadata if a future control-flow model needs it.

Database/model validation should prevent edges from connecting nodes belonging to different workflows. The graph validator should additionally check cycles and other graph-level invariants. Do not rely only on serializer validation for database integrity.

#### WorkflowVersion

Likely responsibilities:

- Workflow reference and monotonically increasing version number within that workflow.
- Immutable published snapshot.
- Publication timestamp and publisher metadata where appropriate.
- Optional validation/compilation metadata.

The precise fields and storage type are not yet decided. A published snapshot must be treated as immutable by application behavior. Consider transaction boundaries and uniqueness constraints for version numbering.

#### Execution (future separate domain)

An execution should reference a specific `WorkflowVersion` and track its own lifecycle. It should not be folded into the editable workflow model. Execution and per-node execution records are future scope, not the first implementation task.

## 9. Suggested implementation roadmap

The sequence below is a guide. Reassess it against the current code as implementation proceeds.

### Phase A — Workflow domain and persistence

- Agree on `Workflow` ownership and lifecycle.
- Implement `Workflow` model, constraints, admin registration if appropriate, and model tests.
- Implement node persistence and tests.
- Implement edge persistence and tests.
- Add database constraints for relationships and uniqueness where possible.

### Phase B — Workflow application logic and APIs

- Define service/application-layer responsibilities.
- Implement create, retrieve, update, list, and delete/archive behavior as appropriate.
- Add organization-scoped authorization and object-level permission checks.
- Keep serializers focused on transport validation; keep domain/application rules out of oversized API views.
- Use the established response and exception conventions.

### Phase C — Graph validation and publishing

- Define a stable in-memory graph representation.
- Validate references, node types, node configs, graph structure, and cycles.
- Use topological sorting or an equivalent dependency analysis for the initial DAG model.
- Compile a validated definition into an immutable version snapshot.
- Publish transactionally and enforce version numbering/immutability invariants.

### Phase D — First synchronous execution engine

- Define a small set of real node types.
- Implement a node registry.
- Define execution and node execution states.
- Build an execution context and simple dependency scheduler.
- Execute a small acyclic workflow synchronously first, with thorough tests.
- Persist results and errors.

### Phase E — Background execution and reliability

- Integrate Celery and Redis.
- Enqueue execution after the required database state is safely persisted.
- Address transaction/queue consistency, duplicate task delivery, and idempotency.
- Add retries, backoff, timeouts, cancellation, and recovery incrementally.

### Phase F — Real-time updates and frontend

- Define and persist meaningful execution events where necessary.
- Add Channels consumers and authorization for WebSocket subscriptions.
- Build the React + TypeScript workflow editor.
- Connect workflow APIs and real-time execution monitoring.

### Phase G — Hardening

- Improve RBAC, auditability, structured logs, metrics, and tracing.
- Add integration and concurrency tests.
- Consider checkpointing/resumability and more advanced parallel/branch/join behavior.
- Document operational setup and deployment.

## 10. Engineering conventions and decisions

These guidelines should be followed unless the existing codebase establishes a deliberate, better convention.

### General

- Inspect the current implementation before editing. Do not overwrite existing functionality based only on this README.
- Work incrementally. Do not generate the entire roadmap in one change.
- Explain the reasoning behind non-obvious architectural choices.
- Add tests with each meaningful behavior change.
- Run the relevant tests and then the full test suite.
- Prefer simple, explicit implementations over speculative frameworks.
- Do not claim a feature works until its behavior has been tested.

### Django and DRF

- Use the project's existing settings split and app structure.
- Use `settings.AUTH_USER_MODEL` for user relationships.
- Respect existing organization boundaries and permissions.
- Keep API views thin; put reusable application/domain operations in an appropriate service/application layer.
- Do not introduce ViewSets or a new API style without checking the current project convention.
- Reuse the shared response helpers and exception hierarchy where appropriate.
- Preserve DRF's default exception handling for exceptions not owned by FlowForge.
- Use named URL reversals in tests instead of hardcoding URL prefixes.
- Add DB constraints for invariants that must hold regardless of the API entry point.

### Data and workflow graph

- Separate editable workflow definitions from immutable published versions.
- Ensure each execution is pinned to a particular published version.
- Do not mutate published snapshots.
- Keep workflow and execution domains distinct.
- Validate graph-level rules in a dedicated domain/application component rather than burying all logic in serializers or model `save()` methods.
- Start with DAG execution. Do not claim arbitrary cyclic graphs or full Temporal-like durability until explicitly implemented and tested.

### Errors and API responses

- Generic errors belong in `shared`; domain-specific error codes belong in their domain.
- Specialized exception classes should fix their semantic code and HTTP status.
- Avoid allowing a `NotFoundError` to be instantiated with an unrelated error code or status.
- Keep the shared response envelope consistent.

### Logging and request context

- Use Python's standard `logging` module and module-level loggers (`logging.getLogger(__name__)`).
- Do not use `print()` for application diagnostics.
- Use the request ID filter/ContextVar mechanism already implemented.
- Keep request-context setup and cleanup in middleware; always reset the ContextVar token in `finally`.
- Do not log secrets, credentials, JWTs, passwords, or sensitive user data.
- Remember that ContextVar request context does not automatically propagate through every Celery/message boundary. Explicitly propagate a correlation ID when asynchronous execution is implemented.

### Tests

- Prefer pytest functions and the project's current pytest-django setup.
- Use unit tests for isolated logic and APIClient/Django test client for request-pipeline integration tests.
- Test success, failure, edge cases, authorization, and database constraints as relevant.
- Do not manually call one pytest test function from another; pytest discovers tests independently.
- Do not assert implementation details when a public behavior/contract can be tested instead.

## 11. Instructions for Codex and other coding agents

Use this section as the operating instructions when working in the FlowForge repository.

1. **Read before writing.** Inspect the relevant files, imports, settings, migrations, and tests before proposing edits.
2. **Treat the repository as the source of truth.** This README captures project direction and known history, but code may have changed. If actual code differs, report the discrepancy and inspect it; do not blindly force the README onto the repository.
3. **Distinguish implemented from planned.** Do not describe a planned feature as complete. Do not create files for future phases unless the current task requires them.
4. **Make small, reviewable changes.** Implement one coherent feature at a time. Avoid broad refactors unless requested and justified.
5. **Explain design choices.** For model relationships, constraints, transactions, concurrency, and service boundaries, explain why the design is appropriate and what alternatives were considered.
6. **Preserve the user's learning process.** The project owner wants to implement and understand the system, not simply receive a large AI-generated codebase. Prefer explaining the next small task, reviewing the user's implementation, and providing focused corrections. If asked to implement a complete file, provide it with an explanation.
7. **Do not invent existing behavior.** Inspect `models.py`, `apps.py`, `urls.py`, settings, and migrations before making assumptions.
8. **Do not overengineer.** Build the smallest correct design that supports the current milestone and leaves reasonable extension points.
9. **Test changes.** Run relevant tests and the full suite where practical. On Windows, if `uv run pytest` is blocked by Application Control, try `uv run python -m pytest`; do not advise disabling Windows security controls as a first response.
10. **Report completion honestly.** State files changed, design implications, commands run, and actual test results. Explicitly mention anything not tested.
11. **Avoid irreversible changes without review.** Be especially careful with migrations, user-model changes, deletion behavior, published-version immutability, and data migrations.
12. **Do not add secrets.** Use environment variables and examples; never commit actual credentials or tokens.

### Current Codex task

The next task is **not** to implement the whole workflow system. Begin by inspecting the current workflow and organization app files, settings, and migrations. Then propose the first `Workflow` model with its ownership, lifecycle, constraints, and relationships. Wait for agreement on the design or present a small, well-reasoned first implementation if explicitly asked. Add tests and run the suite before proceeding to nodes and edges.

## 12. Current status summary

| Area | Status |
|---|---|
| Repository and backend skeleton | Exists; inspect current code before extending |
| Shared API response helpers | Implemented and tested |
| Shared exception hierarchy | Implemented and tested |
| Global DRF exception handler | Implemented and integration-tested |
| Request ID middleware | Implemented and integration-tested |
| Request ID logging context/filter | Implemented; full suite most recently reported passing |
| Django logging configuration | Added; full suite most recently reported passing |
| Workflow data models | Not yet designed/confirmed in this project discussion |
| Node and edge graph persistence | Planned |
| Graph validation | Planned |
| Workflow publishing/version snapshots | Planned |
| Execution engine | Planned |
| Celery/Redis execution integration | Planned |
| Channels/WebSocket execution updates | Planned |
| React/TypeScript visual editor | Planned |

The latest user-provided test result was **17 passed**. Re-run the tests in the current environment before making further changes.

---

## 13. Useful commands

Run tests on Windows:

```powershell
uv run python -m pytest
```

Run the development server:

```powershell
uv run python manage.py runserver
```

Inspect workflow module structure:

```powershell
tree .\modules\workflows /F
```

Inspect organization module structure:

```powershell
tree .\modules\organizations /F
```

Check the configured Django user model:

```powershell
uv run python manage.py shell -c "from django.conf import settings; print(settings.AUTH_USER_MODEL)"
```

The observed value at the time this README was prepared was `auth.User`.

---

**North star:** FlowForge should turn a user-defined workflow graph into a validated, versioned, observable execution that handles failures deliberately. Build that capability incrementally, preserve the separation between definitions and executions, and make every architectural decision understandable and testable.
