---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-04-04'
inputDocuments:
  - '_bmad-output/planning-artifacts/prd.md'
  - '_bmad-output/planning-artifacts/ux-design-specification.md'
  - '_bmad-output/project-context.md'
  - 'docs/index.md'
  - 'docs/project-overview.md'
  - 'docs/technology-stack.md'
  - 'docs/source-tree-analysis.md'
  - 'docs/integration-architecture.md'
  - 'docs/development-guide.md'
  - 'docs/architecture-management-api.md'
  - 'docs/architecture-authorization-api.md'
  - 'docs/architecture-management-ui.md'
  - 'docs/architecture-guardian-lib.md'
  - 'docs/architecture-authorization-client.md'
  - 'docs/data-models-management-api.md'
  - 'docs/data-models-authorization-api.md'
  - 'docs/api-contracts-management-api.md'
  - 'docs/api-contracts-authorization-api.md'
  - 'docs/api-contracts-management-ui.md'
  - 'docs/ui-components-management-ui.md'
  - 'docs/state-management-management-ui.md'
  - 'docs/devel/concept_proposal.md'
  - 'docs/devel/Integrate_Guardian.md'
  - 'docs/devel/management_ports/README.md'
  - '/home/dtroeder/git/decision-records/dev/0007-log-messages.md'
  - 'ABAC-system.png'
  - '2025-11-27_RAM_Strategy_v2.md'
  - '/home/dtroeder/git/dev/docs/nubus-docs/docs/nubus-kubernetes-architecture/components/authorization-service.rst'
  - '/home/dtroeder/git/dev/libraries/port-loader/AGENTS.md'
  - '/home/dtroeder/git/dev/libraries/port-loader/_bmad-output/project-context.md'
  - '/home/dtroeder/git/dev/libraries/univention-veb/AGENTS.md'
  - '/home/dtroeder/git/dev/libraries/univention-veb/_bmad-output/project-context.md'
workflowType: 'architecture'
project_name: 'guardian'
user_name: 'Nubus Core team'
date: '2026-04-04'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

46 functional requirements spanning 10 categories. The architecturally significant clusters are:

1. **Entity Lifecycle Management (FR1-FR6):** Extends existing CRUD with DELETE operations for all 7 entity types (apps, namespaces, roles, contexts, permissions, conditions, capabilities). Currently only capabilities support DELETE. This is the highest-impact structural change to the Management API -- it requires referential integrity checks across the entire entity graph before any deletion can proceed.

2. **Multi-Role Capability Assignment (FR7-FR10):** Transforms the capability data model from a single `role_id` FK to a many-to-many relationship. This cascades through all three model layers (domain dataclass, Pydantic router model, SQLAlchemy ORM), the OPA `roleCapabilityMapping` bundle format, the Management UI's capability editing flow, and the authorization-client library.

3. **Authorization Decisions (FR11-FR15):** The existing Authorization API endpoints are unchanged in contract. The architectural concern is performance under the new multi-role capability model -- OPA's data bundle structure and Rego evaluation paths may need optimization to maintain the <20ms p95 target.

4. **Permission Reporting & Diagnostics (FR16-FR19):** Entirely new functionality with no existing endpoints. The per-user permission query requires a new Management API endpoint that traverses the full authorization chain (roles -> capabilities -> conditions -> permissions) for a given user. The CISO permission matrix report requires a cross-namespace aggregation view. Both demand new API contracts, business logic functions, and UI views.

5. **Logging & Observability (FR20-FR26):** Cross-cutting concern affecting all components. Structured logging conforming to Univention ADRs, configurable log levels per component, PII constraints (IDs at INFO, PII at TRACE only), health/readiness probes, and Prometheus metrics. The OPA decision log PII spike is a prerequisite research task.

6. **Configuration & Deployment (FR27-FR31):** Configurable SQL database URI, secured OPA bundle endpoint, OIDC client configuration fix, API versioning, and stateless horizontal scaling. These are infrastructure-level decisions affecting Helm charts, App Center packaging, and docker-compose configurations.

7. **Support & Operations Tooling (FR32-FR34):** A new CLI tool for dump/restore of Guardian configuration. This is a standalone component (likely Python, using the Management API) that must work against both App Center and Kubernetes deployments.

8. **Management UI (FR35-FR39):** Major UI evolution from generic ListView/EditView to split-panel layout with entity tree, dedicated CapabilityEditor, PermissionTraceView, and impact preview for DELETE operations. The UX specification defines 10+ new custom components.

9. **Authorization Client Library (FR40-FR41):** Must be updated to support new API features (multi-role capabilities, new endpoints). Remains sync-only Python with `requests`.

10. **Documentation (FR42-FR46):** Four deliverable documents (Integration Guide, Support Handbook, Administrator Guide, Operations Guide) plus auto-generated OpenAPI specs.

**Non-Functional Requirements:**

28 NFRs across 7 categories that directly constrain architectural decisions:

- **Performance (NFR1-NFR6):** Authorization <20ms p95 (excl. UDM lookup), Management CRUD <50ms p95, bundle regeneration <30s, UI renders <2s. These set hard boundaries on data access patterns, caching strategies, and bundle generation architecture.

- **Security (NFR7-NFR12):** Authenticated OPA bundle endpoint, OIDC on all Management API/UI access, PII restricted to TRACE level with CI enforcement, API versioning for integration stability, referential integrity on DELETE, no credential exposure in CLI dump output.

- **Scalability (NFR13-NFR16):** Stateless components, support for 20 apps / 100 roles / 500 capabilities / 500 permissions, Authorization API + OPA sidecar scaling pattern, database connection pooling.

- **Reliability (NFR17-NFR20):** OPA continues serving from cache when Management API is down, bundle sync failure detection, backward-compatible Alembic migrations, accurate health/readiness probes.

- **Integration (NFR21-NFR24):** <20ms with 20 registered apps, clear UDM failure errors (not silent denials), clear OIDC 401 errors, concurrent Management API request handling.

- **Test Quality (NFR25-NFR28):** 100% unit test coverage maintained, integration tests for all endpoints, PII leak detection in CI, exhaustive referential integrity DELETE tests.

**Stakeholder Impact Mapping (Phase 1):**

Not all Phase 1 requirements serve the same consumers. The dependency ordering for which stakeholders are unblocked:

| Requirement Cluster | Primary Consumer Unblocked | Secondary Consumers |
|---|---|---|
| DELETE with referential integrity (FR1-FR6) | All -- production readiness blocker (RAM Strategy MUST) | Support/operations teams |
| Multi-role capabilities (FR7-FR10) | Portal (tiles depend on shared capabilities) | Future UDM delegated admin |
| Logging & observability (FR20-FR26) | Operations/CISO (audit trail requirement) | Support, developers |
| Configuration & deployment (FR27-FR31) | Kubernetes operators, App Center admins | All consumers (OIDC fix) |
| Permission reporting (FR16-FR19) | CISO/compliance, school administrators | Support teams |
| CLI tooling (FR32-FR34) | Support department | Operations |
| Management UI (FR35-FR39) | Guardian administrators, app administrators | School administrators (via future domain-specific UIs) |
| API versioning (FR30) | UCS@school (stability guarantee for Aug integration) | All future integrators |

**Scale & Complexity:**

- Primary domain: Full-stack distributed authorization platform
- Complexity level: High / Enterprise
- Existing architectural components: 5 (Management API, Authorization API, guardian-lib, authorization-client, Management UI) + OPA + infrastructure
- New components to architect: CLI dump/restore tool, per-user permission query endpoint, DELETE with referential integrity system, impact preview API, CapabilityEditor + PermissionTraceView + entity tree UI components
- Estimated total architectural decision areas: 12-15

**Risk Note:** The RAM Strategy document (2025-11-27) estimates 160 PT for production readiness. This estimate was produced by Daniel and Ole and has *not been confirmed by a development team*. It should be treated as a rough order-of-magnitude indicator, not a planning input. Individual feature estimates within the RAM Strategy use T-shirt sizes (S: <10 PT, M: 10-20 PT, L: 21-50 PT) at *maximum* values, and explicitly exclude application-specific Management UIs and performance testing.

### Technical Constraints & Dependencies

**Hard Constraints (non-negotiable):**

1. **Hexagonal architecture must be preserved.** All new features must follow ports-and-adapters. Business logic in `business_logic.py` only. Three-model-layer discipline (domain dataclass, Pydantic router, SQLAlchemy ORM).

2. **port-loader 1.2.0 (exact pin).** The entire adapter loading and DI system depends on this specific version. Adapter registration via Poetry entry points in `pyproject.toml`. Adapter selection via `GUARDIAN__<SERVICE>__ADAPTER__<PORT_NAME>` environment variables.

3. **Python 3.11+ / FastAPI / SQLAlchemy 2 (async) / Pydantic v2.** Version constraints differ between services: FastAPI `<0.200` in management-api vs `^0.135.1` in authorization-api. **This divergence is a concrete cross-cutting constraint** -- any shared middleware, OIDC integration, or API versioning pattern must verify feature availability in *both* pinned ranges. The authorization-api pin is significantly older and may lack features available in the management-api's range.

4. **Vue 3 Composition API / TypeScript / univention-veb component library.** All UI changes must use VEB components as atoms, follow the existing Stylus/CSS custom property theming, and support light/dark modes.

5. **OPA with Rego policies.** Policy bundle generation from Management API, OPA polling for bundles. The Cerbos evaluation (from RAM Strategy) is explicitly deferred to Phase 3.

6. **Dual deployment targets.** Every configurable feature must work on both Kubernetes Helm charts and UCS App Center. No Kubernetes-only features in MVP.

7. **Backward compatibility.** API v1 endpoints must remain stable through 2026. UCS@school's August integration must not break when Portal/UDM changes are made later.

8. **AGPL-3.0-only license.** Every source file requires REUSE-compliant headers.

**External Dependencies:**

- **UDM REST API:** Authorization API's "with-lookup" endpoints depend on UDM availability and response time. UDM is synchronous and sequential -- this is a known performance bottleneck independent of Guardian.
- **Keycloak:** OIDC authentication for Management API and UI. Client configuration must be correctly provisioned during both App Center install/upgrade and Helm deployment.
- **OPA (v1.11.0):** Policy evaluation engine. Bundle polling interval (10-15s) combined with async bundle regeneration (<30s) defines the one-minute policy propagation SLA.
- **PostgreSQL:** Production database. SQLite for development. Configurable URI is a new MVP requirement.

**Existing Technical Debt (from project-context.md):**

- `bundle_server.py` uses `asyncio.create_subprocess_shell` with f-string commands (shell injection risk)
- `guardian_lib/adapters/authentication.py` uses synchronous `requests.get` inside `async def` (event loop blocking)
- Frontend string-matching error detection (`data.ts:177`) instead of typed error codes
- Correlation ID middleware accepts arbitrary strings without validation
- Authorization API's `transform_exception` leaks internal error details in 500 responses
- Namespace business logic accepts concrete `FastAPINamespaceAPIAdapter` instead of abstract port

### Cross-Cutting Concerns Identified

1. **Structured Logging with PII Constraints:** Affects Management API, Authorization API, OPA, and the new CLI tool. The Univention logging ADR (0007) mandates structured logging with event/data separation, PII restricted to TRACE level, and configurable sensitive data logging via dedicated configuration options. An OPA decision log PII spike must complete before the logging implementation. CI must include PII leak detection tests with configurable forbidden attribute lists.

2. **API Versioning:** Both Management API and Authorization API must add version prefixes to URL paths (`/v1/`). This is a routing-level change that affects all 50+ existing endpoints, the Management UI's `ApiDataAdapter`, and the authorization-client library. Must be backward-compatible -- existing unversioned paths should continue to work during a transition period.

3. **Referential Integrity on DELETE:** Every entity type participates in a dependency graph (app -> namespace -> role/permission/context/condition, capability -> role + permissions + conditions). DELETE operations must validate the entire dependency chain before proceeding. The UI requires impact preview data (affected entity counts, user impact) from the API *before* the user confirms deletion. This requires a new "dry-run" or "impact query" API pattern.

4. **Multi-Role Capability Data Model Change:** The current `capability.role_id` FK becomes a many-to-many `capability_role` join table. This affects: SQL schema (Alembic migration), domain model (`Capability.role` becomes `Capability.roles: list[Role]`), router models, OPA bundle generation (`roleCapabilityMapping` keys now reference shared capabilities), capability persistence adapter, Management UI capability editor, and authorization-client. **Migration note:** The forward migration (FK -> join table) is straightforward. The *reverse* migration is lossy -- a capability assigned to multiple roles can only preserve its first role assignment on downgrade. This makes the multi-role capability change a **breaking downgrade**. This must be documented as a one-way schema migration and communicated to operations teams. **Cerbos consideration:** The join table structure and the resulting changes to `roleCapabilityMapping` should be designed with awareness that a future Cerbos migration (Phase 3) may restructure how capabilities map to policies. Avoid encoding OPA-specific assumptions into the join table schema itself.

5. **Configuration Parity Across Deployment Targets:** Every new configuration option (database URI, log levels, OIDC settings, bundle server auth, health probe paths) must be exposed in both Helm chart values and App Center settings. Environment variable naming follows `GUARDIAN__<SERVICE>__<SECTION>__<KEY>` convention.

6. **Security Hardening:** OPA bundle endpoint authentication, OIDC client configuration fix, PII protection in logs, no credential exposure in CLI output. The bundle endpoint is particularly critical -- policy bundles encode the complete authorization configuration and must not be accessible without authentication.

7. **Performance Budget Enforcement:** The <20ms authorization check target, <50ms Management CRUD target, and <30s bundle regeneration target must be validated in CI. Multi-role capabilities may increase OPA evaluation time (more capabilities per role in the mapping). Performance benchmarking infrastructure needs architectural consideration.

### Architectural Decision Dependency Ordering

Decisions should be made in this sequence, as later decisions depend on earlier ones:

1. **Data model decisions** (multi-role capability schema, DELETE referential integrity model) -- these define the shape of all data flowing through the system
2. **API surface decisions** (versioning strategy, new endpoints for permission trace and impact preview, DELETE contract) -- these depend on the data model and define the contract between components
3. **UI and tooling decisions** (CapabilityEditor design, PermissionTraceView scope, CLI architecture) -- these consume the API contracts
4. **Infrastructure decisions** (bundle endpoint security, logging architecture, deployment configuration, metrics) -- these are cross-cutting but can be layered on independently

**PermissionTraceView scope clarification:** Two distinct capabilities exist under this umbrella:
- **Configuration trace** (Phase 1): Reconstructs the authorization chain from Management API data -- given a user's roles, show which capabilities could grant which permissions, with condition details. This is a database query against the Management API's own data, not an OPA interaction.
- **Runtime decision trace** (Phase 2/3): Captures actual OPA evaluation paths showing *why* a specific authorization request was permitted or denied. This requires OPA decision logging, has PII implications, and adds performance overhead. Deferred.

## Starter Template Evaluation

### Assessment: Brownfield Project -- No Starter Template Applicable

Guardian is an existing production system (v3.0.6) with a fully established technology stack. No starter template, CLI scaffolding, or boilerplate selection is required. All technology choices are inherited from the existing codebase. This section documents the current stack, distinguishing between **locked-in decisions** (structurally embedded, cost-prohibitive to change) and **evolutionary opportunities** (incremental improvements achievable within the existing system).

### Locked-In Technology Decisions

These are structural choices embedded throughout the codebase. Changing any of them would constitute a rewrite, not an evolution:

**Backend (Management API + Authorization API):**

- Python 3.11+, FastAPI, SQLAlchemy 2 (async), Pydantic v2, Alembic
- port-loader 1.2.0 for dependency injection (hexagonal architecture)
- Poetry for dependency management and packaging
- loguru for structured logging (not stdlib logging)

**Policy Engine:**

- Open Policy Agent (OPA) v1.11.0 with Rego policies
- Bundle server hosted within Management API process
- OPA polling for bundle updates (10-15s interval)

**Frontend (Management UI):**

- Vue 3 Composition API with TypeScript
- univention-veb component library (Stylus, BEM-like naming, dark/light theming)
- Vite build tooling, Yarn 1.22.x package manager
- Pinia for state management with adapter pattern

**Shared Libraries:**

- guardian-lib: shared Python models and adapters (authentication, logging). **Coordinated release constraint:** Changes to guardian-lib interfaces affect both Management API and Authorization API. Any guardian-lib modification requires coordinated testing and release across both services.
- authorization-client: sync-only Python HTTP client (`requests`) for Authorization API. **Known limitation:** Async consumers (e.g., Portal, UDM) must wrap calls in `asyncio.to_thread()`. The PRD does not require making it async, but this is a known friction point for integration.

**Deployment:**

- Kubernetes: Helm charts
- UCS: App Center packaging
- Docker Compose for local development
- PostgreSQL (production), SQLite (development)

### Evolutionary Opportunities

These are not locked-in -- they represent accumulated drift or directional improvements achievable within the existing architecture:

1. **FastAPI version pin harmonization.** Management API pins `<0.200`, Authorization API pins `^0.135.1` (pre-Pydantic-v2-native FastAPI). Any shared middleware, OIDC integration, or API versioning pattern must verify feature availability in the Authorization API's older range. **Recommendation:** Align both services to a shared minimum pin during Phase 1 to reduce cross-cutting risk. Verify actual minimum FastAPI version required by authorization-api before setting the new range.

2. **guardian-lib async migration.** `guardian_lib/adapters/authentication.py` uses synchronous `requests.get` inside `async def`, blocking the event loop. **Directional intent:** guardian-lib should evolve toward fully async adapters (using `httpx` or `aiohttp`). This may not be a Phase 1 deliverable, but the architecture document establishes the direction so that new adapters added in Phase 1 follow the async pattern, and existing adapters can be migrated incrementally.

3. **authorization-client async variant.** The client library is sync-only by design (`requests`). If Phase 2/3 consumers require native async integration, a new async client adapter could be added behind the existing port interface, following the hexagonal pattern. No action required in Phase 1.

### Open Technology Decisions

The following new components do *not* inherit a locked-in stack and require explicit architectural decisions in Step 4:

- **CLI dump/restore tool (FR32-FR34):** This is a new standalone component. Technology choices are open -- Python with `click` or `typer`, using the existing `authorization-client` or a standalone `httpx`-based tool, output format (JSON, YAML), credential handling approach.

### Architectural Patterns Established by Existing Codebase

These patterns are non-negotiable for all new development:

- **Hexagonal / ports-and-adapters architecture** across all components
- **Three-model-layer discipline**: domain @dataclass, Pydantic router model, SQLAlchemy ORM model
- **Thin routers**: routers wire dependencies and delegate to `business_logic.py`
- **Adapter registration via Poetry entry points** (`pyproject.toml`) and runtime selection via environment variables (`GUARDIAN__<SERVICE>__ADAPTER__<PORT_NAME>`)
- **Frontend adapter store pattern**: Pinia store with switch/case on configuration strings for adapter selection

### Test Infrastructure Baseline

**Python (established):**

- pytest with pytest-asyncio, pytest-mock, pytest-cov
- 100% unit test coverage target enforced in CI
- Integration tests for API endpoints (Management API + Authorization API)
- Fixtures and factory patterns documented in project-context.md

**Frontend (partially established):**

- Vitest configured for unit tests, Playwright configured for E2E
- Management UI has existing test directories and some test coverage
- univention-veb component library notes "no test files exist yet" -- test patterns for VEB-based components are not yet established
- The UX spec introduces 10+ new Guardian-specific components that will need test coverage

**Infrastructure gaps (must be addressed):**

- **PII leak detection in CI (NFR28):** No existing CI job. Requires a new pipeline step with configurable forbidden attribute lists to scan log output and test assertions for PII exposure above TRACE level.
- **Performance benchmarking:** No existing CI infrastructure for validating the <20ms / <50ms / <30s targets. Needs architectural consideration for how and where to run performance tests.
- **Referential integrity DELETE tests (NFR28):** No existing patterns -- this is entirely new test territory covering the full entity dependency graph.

### Code Quality (Established)

- pre-commit hooks: Black, Ruff, mypy, Bandit (run via `pre-commit run --all-files`, not installed as dev deps)
- REUSE-compliant AGPL-3.0-only SPDX headers on all files
- Zero-warning lint policy on frontend (`--max-warnings=0`)

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**

1. Multi-role capability schema: simple join table, `roles: list[Role]`, PUT + RFC 6902 JSON PATCH
2. DELETE referential integrity: block-on-reference, separate preview endpoints, full transitive closure
3. API versioning: URL path prefix `/v1/`, alias with deprecation warning, no breaking changes per version
4. Permission trace: Management API, POST with actor UDM object + explicit roles, nested role->capability->permission+condition response
5. OPA bundle security: bearer token, Kubernetes Secret + env var provisioning
6. CLI tool: Python + typer, httpx, JSON (with --format yaml), single file, dedicated /v1/dump endpoint

**Important Decisions (Shape Architecture):**

7. Impact preview: `GET /v1/{entity_type}/{id}/impact` sub-resource pattern
8. Structured logging: keep existing format, sanitized correlation ID pass-through, PII convention + CI enforcement
9. Health probes: separate `/healthz`, `/readyz`, `/startupz` endpoints with dependency-aware checks
10. Prometheus metrics: `/metrics` on both services, custom per-metric histogram buckets

**Deferred Decisions (Post-Phase 1):**

- Runtime decision trace (OPA decision logging) -- Phase 2/3
- Cerbos evaluation -- Phase 3
- authorization-client async variant -- as needed
- Internal consumer migration to `/v1/` paths -- Phase 2

### Decision 1: Multi-Role Capability Schema

- **Category:** Data Architecture
- **Decision:** Simple join table `capability_role(capability_id, role_id)` with composite PK. Domain model changes from `Capability.role: Role` to `Capability.roles: list[Role]` (full Role objects). Alembic migration seeds join table from existing `role_id` FK, then drops the column.
- **Rationale:** Standard M2M pattern, consistent with existing domain model conventions (capabilities already hold lists of permissions and conditions). No metadata needed on the relationship.
- **Affects:** SQL schema, domain models, Pydantic router models, capability persistence adapter, OPA bundle generation, Management UI CapabilityEditor, authorization-client
- **Migration:** Forward migration is straightforward. Reverse migration is lossy (multi-role assignments collapse to first role). **Breaking downgrade** -- must be documented as one-way schema migration.

**Update Semantics:**

- **PUT** replaces the entire capability including the full roles list (consistent with existing PUT semantics)
- **RFC 6902 JSON PATCH** introduced for granular add/remove operations on the roles list
- JSON PATCH is established as a **general architectural pattern** available on any entity with list-type fields, not capability-specific. This means a new PATCH handler pattern in the router layer that parses RFC 6902 operations, with business logic validation that the resulting state is valid. Existing simple PATCH endpoints coexist during transition.

**OPA Bundle Impact:**

- `roleCapabilityMapping` keeps role-keyed format: each role maps to its capabilities, shared capabilities appear under multiple roles
- Bundle size increases slightly with duplication, negligible at Guardian's scale (500 capabilities max per NFR)

### Decision 2: DELETE Referential Integrity

- **Category:** Data Architecture / API Design
- **Decision:** Block-on-reference. DELETE is refused if any dependent entity exists. Client must delete bottom-up through the dependency graph.
- **Rationale:** Safest approach for an authorization system. Accidental cascade deletion of an app's entire permission structure could lock users out of services. Block-on-reference makes destructive operations explicit and deliberate.
- **Affects:** All 7 entity types (apps, namespaces, roles, contexts, permissions, conditions, capabilities), Management API business logic, Management UI delete confirmation flow

**Impact Preview:**

- Separate preview endpoint per entity type: `GET /v1/{entity_type}/{id}/impact`
- Returns **full transitive closure** of the dependency graph -- all entities at all levels that depend on the target
- Response includes: entity type, identifier (app:namespace:name format), and display name for each affected entity
- At Guardian's scale (NFR13-16), graph traversal is trivially small -- no pagination needed

### Decision 3: API Versioning

- **Category:** API Design
- **Decision:** URL path prefix versioning. All endpoints get `/v1/` prefix. Unversioned paths alias to v1 with `Deprecation` HTTP header in response.
- **Rationale:** Most visible, explicit, industry-standard REST versioning. Alias with deprecation warning allows zero-disruption migration for existing consumers.
- **Affects:** All 50+ endpoints on Management API and Authorization API, Management UI ApiDataAdapter, authorization-client library
- **Version Policy:** "Stable" means no breaking changes within a version. Additive changes (new optional fields, new endpoints) are non-breaking and allowed. Breaking changes require a new version (e.g., v2).
- **Internal Consumer Migration:** Deferred to Phase 2. Management UI and authorization-client continue using unversioned aliases in Phase 1.

### Decision 4: Permission Trace Query (Configuration Trace)

- **Category:** API Design / New Functionality
- **Decision:** New endpoint on Management API: `POST /v1/permissions/trace`. Caller provides actor's UDM object (including roles) in the JSON request body. Management API traverses roles -> capabilities -> conditions -> permissions from its own database.
- **Rationale:** Management API owns all the data needed for configuration trace. POST with explicit actor data keeps Management API free of UDM dependencies and makes the endpoint testable without external services. Supports "what-if" scenarios by allowing arbitrary role sets.
- **Affects:** Management API (new endpoint, new business logic function, new router models), Management UI PermissionTraceView, CLI tool (optional)

**Response Structure:**

```json
{
  "actor": "uid=admin,dc=example",
  "roles": [
    {
      "role": "app:namespace:role_name",
      "capabilities": [
        {
          "capability": "app:namespace:cap_name",
          "permissions": ["app:namespace:perm1", "app:namespace:perm2"],
          "conditions": [
            {
              "condition": "app:namespace:condition_name",
              "parameters": ["..."],
              "relation": "AND"
            }
          ],
          "relation": "AND"
        }
      ]
    }
  ]
}
```

**Scope Clarification:** This is the Phase 1 "configuration trace" only -- it shows what the authorization configuration *would* grant, not what OPA *actually* evaluated at runtime. Runtime decision trace (OPA decision logging) is deferred to Phase 2/3.

### Decision 5: OPA Bundle Endpoint Security

- **Category:** Security / Infrastructure
- **Decision:** Bearer token authentication on the bundle endpoint. Token stored as Kubernetes Secret, mounted via env var (using port-loader's `_FILE` env var suffix for file-based secrets). App Center uses UCR variable or file-based secret.
- **Rationale:** Simplest mechanism that works across both deployment targets. OPA natively supports bearer token in `services[].credentials.bearer.token` configuration. mTLS is stronger but certificate lifecycle management adds unjustified operational complexity for internal service-to-service communication.
- **Affects:** Management API bundle server endpoint (add token validation middleware), OPA configuration (add bearer token), Helm chart values (new secret), App Center settings (new UCR variable)

### Decision 6: CLI Tool Architecture

- **Category:** New Component
- **Decision:** Python + `typer` CLI framework, `httpx` for async HTTP communication with Management API, JSON output format with `--format yaml` flag, single-file dump, dedicated `POST /v1/dump` and `POST /v1/restore` Management API endpoints with centralized credential redaction.
- **Rationale:** Consistent with backend stack (Python). Typer provides modern CLI with minimal code and auto-generated help. httpx enables async parallel entity fetching for dump performance. Centralized redaction at the API level is the only safe approach -- the CLI should not maintain a list of sensitive fields. Single file keeps the tool simple.
- **Affects:** New Python package (likely `guardian-cli`), Management API (new dump/restore endpoints), Helm chart and App Center packaging (optional -- CLI may be a standalone tool)

### Decision 7: Impact Preview API Pattern

- **Category:** API Design
- **Decision:** `GET /v1/{entity_type}/{id}/impact` -- impact as a sub-resource of the entity being previewed.
- **Rationale:** Follows REST convention. Consistent with existing API nesting patterns.

### Decision 8: Structured Logging

- **Category:** Cross-Cutting / Observability
- **Decision:** Keep existing log format unchanged (already satisfies requirements). Correlation ID middleware updated to sanitize pass-through values (strip non-printable characters, enforce length limit) and generate UUID v4 when header is missing or invalid. PII enforcement via naming convention and CI test enforcement only -- no runtime PII filtering infrastructure.
- **Rationale:** Lightest-touch approach. Existing format works. CI PII leak detection job (NFR28) becomes the critical enforcement mechanism with configurable forbidden attribute lists.
- **Affects:** Correlation ID middleware (both APIs), CI pipeline (new PII detection job), developer conventions (documented PII field naming)

### Decision 9: Health/Readiness Probes

- **Category:** Infrastructure / Reliability
- **Decision:** Separate endpoints per probe type following Kubernetes convention.

| Service | `/healthz` (Liveness) | `/readyz` (Readiness) | `/startupz` (Startup) |
|---|---|---|---|
| Management API | Process alive, event loop responsive | DB connection pool healthy, OPA bundle server operational | Initial Alembic migration check passed, first bundle generated |
| Authorization API | Process alive, event loop responsive | OPA sidecar reachable, valid bundle loaded | OPA sidecar responded to first health check |

- **Rationale:** Standard Kubernetes convention. Liveness is cheap (no DB calls), readiness verifies downstream dependencies, startup gates initial traffic until service is ready.
- **Affects:** Both APIs (new route handlers), Helm chart probe configuration, App Center health check configuration

### Decision 10: Prometheus Metrics

- **Category:** Observability / Infrastructure
- **Decision:** `/metrics` endpoint on both Management API and Authorization API. Custom per-metric histogram buckets tuned to performance NFR targets.

**Authorization API Metrics:**

- `guardian_authz_requests_total` (counter, labels: endpoint, status_code)
- `guardian_authz_request_duration_seconds` (histogram, buckets: .001, .005, .01, .015, .02, .025, .05, .1, .25, .5, 1)
- `guardian_authz_opa_evaluation_duration_seconds` (histogram, same fine-grained buckets)
- `guardian_authz_udm_lookup_duration_seconds` (histogram, same fine-grained buckets)

**Management API Metrics:**

- `guardian_mgmt_requests_total` (counter, labels: endpoint, status_code)
- `guardian_mgmt_request_duration_seconds` (histogram, buckets: .01, .025, .05, .1, .25, .5, 1, 2.5, 5)
- `guardian_mgmt_bundle_generation_duration_seconds` (histogram, buckets: 1, 5, 10, 15, 20, 25, 30, 45, 60)
- `guardian_mgmt_bundle_generation_total` (counter, labels: status)

- **Rationale:** Custom buckets give useful resolution around the NFR targets (20ms auth, 50ms CRUD, 30s bundle generation). Default Prometheus buckets lack precision at the 20ms range.
- **Affects:** Both APIs (new metrics middleware), Helm chart (Prometheus scrape annotations), monitoring dashboards

### Decision Impact Analysis

**Implementation Sequence:**

Following the dependency ordering from the context analysis:

1. **Data model first:** Decision 1 (multi-role schema) + Decision 2 (referential integrity model) -- Alembic migrations, domain model changes, persistence adapters
2. **API surface second:** Decision 3 (versioning) + Decision 4 (permission trace) + Decision 6 (dump/restore endpoints) + Decision 7 (impact preview) -- new endpoints, router models, business logic
3. **UI and tooling third:** CapabilityEditor consuming multi-role API, PermissionTraceView consuming trace endpoint, delete confirmation consuming impact preview, CLI tool consuming dump/restore
4. **Infrastructure fourth:** Decision 5 (bundle security) + Decision 8 (logging) + Decision 9 (probes) + Decision 10 (metrics) -- can be layered independently

**Cross-Component Dependencies:**

- Decision 1 (multi-role) cascades to: OPA bundle format, UI CapabilityEditor, authorization-client, CLI dump format
- Decision 2 (DELETE) requires: Decision 7 (impact preview) before UI can implement delete confirmation
- Decision 3 (versioning) affects: all other API decisions (endpoints use `/v1/` prefix)
- Decision 6 (CLI) depends on: Decision 1 (multi-role in dump format), Decision 3 (versioned endpoints), dedicated dump/restore endpoints
- Decision 8 (logging) + Decision 10 (metrics) are independent and can be implemented in parallel with other work
- RFC 6902 JSON PATCH (from Decision 1) establishes a pattern that may be adopted by other entity endpoints over time

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**8 conflict points** identified where AI agents could make different choices based on the new architectural decisions. These patterns supplement the 127 existing rules in `project-context.md`, which continue to govern all naming, style, import, testing, and code quality conventions. The patterns below address only the gaps introduced by the Phase 1 architectural decisions.

### Pattern 1: RFC 6902 JSON PATCH Handler

**Scope:** All entities with list-type fields (capabilities first, extensible to others).

**Router layer:** Single PATCH route per entity with content-type discrimination:
- `Content-Type: application/json` -> existing simple partial update handler
- `Content-Type: application/json-patch+json` -> RFC 6902 handler

**Business logic:** One generic `apply_json_patch(entity, operations)` function that applies all operations and validates the resulting state after all operations are applied (not after each individual operation). This function lives in `guardian-lib` or a shared utility module so all entities use the same implementation.

**Validation:** State validation occurs once, after all patch operations are applied. If the resulting state is invalid, the entire patch is rejected -- no partial application.

### Pattern 2: New Endpoint Organization

New endpoints introduced by the architectural decisions follow this placement rule:

| Endpoint Type | Location | Rationale |
|---|---|---|
| Impact preview (`GET .../impact`) | Each entity's existing router file in `routes/` | Sub-resource of the entity -- belongs with its CRUD routes |
| Health probes (`/healthz`, `/readyz`, `/startupz`) | New `routes/operations.py` | Cross-cutting operational concern, not entity-specific |
| Prometheus metrics (`/metrics`) | New `routes/operations.py` | Same as health probes -- operational infrastructure |
| Dump/restore (`/v1/dump`, `/v1/restore`) | New `routes/admin.py` | Administrative operations, distinct from entity CRUD |
| Permission trace (`/v1/permissions/trace`) | New `routes/permissions.py` | New functional domain, not a sub-resource of an existing entity |

**Principle:** CRUD + sub-resources stay with the entity router. Cross-cutting operational concerns get their own router files. New functional domains get new router files.

### Pattern 3: Entity Dependency Graph Traversal

**Impact preview and DELETE validation** both need to traverse the entity dependency graph. This is implemented once, not per-entity.

**Declarative dependency map** defined in `business_logic.py`:

```python
ENTITY_DEPENDENCY_GRAPH = {
    "app": ["namespace"],
    "namespace": ["role", "permission", "context", "condition"],
    "role": ["capability"],
    "permission": ["capability"],
    "context": ["capability"],
    "condition": ["capability"],
    "capability": [],
}
```

**Generic traversal function** walks this map for any entity type, collecting the full transitive closure. Both impact preview and DELETE validation call the same function. No agent should implement per-entity graph traversal -- add new entity types to the map instead.

### Pattern 4: Bundle Endpoint Bearer Token Authentication

**Coexistence with OIDC:** The bundle endpoint uses bearer token auth while all other Management API endpoints use OIDC. This is handled via route-specific FastAPI `Depends()` injection -- no global middleware changes.

**Implementation follows hexagonal pattern:**
- Define `BundleAuthenticationPort` ABC
- Implement `BearerTokenBundleAuthenticationAdapter` that performs constant-time string comparison against the configured secret
- Register via Poetry entry point in `pyproject.toml`
- Inject as `Depends(verify_bundle_token)` on the bundle route only

The OIDC auth dependency continues to be injected on all other routes as today. No global middleware changes.

### Pattern 5: Dump/Restore Format Contract

**Dump file structure** uses a flat top-level structure keyed by entity type, with metadata header:

```json
{
  "format_version": "1",
  "guardian_version": "4.0.0",
  "exported_at": "2026-04-04T12:00:00Z",
  "apps": [...],
  "namespaces": [...],
  "roles": [...],
  "permissions": [...],
  "contexts": [...],
  "conditions": [...],
  "capabilities": [...]
}
```

**Entity representation:** Uses Pydantic router model serialization (the same format the API returns). This is the contract external consumers already know.

**Restore ordering:** The restore endpoint handles topological ordering internally. The dump file does not guarantee ordering. Agents implementing restore must process entities in dependency order: apps -> namespaces -> conditions -> permissions -> contexts -> roles -> capabilities.

### Pattern 6: Prometheus Metrics Integration

**Library:** `prometheus-client` (official Python client). No framework-specific wrappers.

**Metric definition:** Module-level constants in a dedicated `metrics.py` file per service. One file per service, not scattered across modules.

**Custom timing:** Context manager pattern consistently:

```python
with BUNDLE_GENERATION_DURATION.time():
    await generate_bundle()
```

**Endpoint:** Standard `make_asgi_app()` mount at `/metrics`. Not a FastAPI route -- a mounted ASGI sub-application.

**No port/adapter abstraction** for metrics. Metrics are infrastructure, not business logic.

### Pattern 7: Health Probe Response Format

**Response format:** JSON with individual check status. HTTP 200 for healthy, 503 for unhealthy. Kubernetes reads the status code; the JSON body is for human debugging.

**Liveness** (`/healthz`):
```json
{"status": "healthy"}
```
No dependency checks. Must never block on external services.

**Readiness** (`/readyz`) and **Startup** (`/startupz`):
```json
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy", "latency_ms": 2},
    "bundle_server": {"status": "healthy"}
  }
}
```

**Check execution:** Run all checks, report aggregate. Do not fail-fast on the first unhealthy check -- report all statuses so operators can see the full picture.

**Timeout:** Each probe handler enforces its own internal timeout (3s per individual check) to avoid hanging on a slow dependency. If a check times out, report it as `{"status": "timeout"}`.

### Pattern 8: API Versioning Route Registration

**Prefix application:** Top-level `APIRouter(prefix="/v1")` that includes all entity routers. Single point of control -- individual router files remain unaware of versioning.

**Unversioned aliases:** Mount the same router a second time without the `/v1/` prefix.

**Deprecation header:** Lightweight middleware that adds the `Deprecation` HTTP header when the request path does not start with `/v1/`. Applied globally, not per-route. This ensures every unversioned alias consistently returns the deprecation signal.

**Result:** Every new endpoint automatically gets both versioned and unversioned paths. No route duplication in router files. Deprecation is applied uniformly.

### Enforcement Guidelines

**All AI Agents MUST:**

- Follow the 127 rules in `project-context.md` for all naming, style, import, testing, and quality conventions
- Follow these 8 patterns for all new functionality introduced by the Phase 1 architectural decisions
- When in doubt, check existing code in the same component for precedent before inventing a new pattern
- When adding a new entity type, add it to `ENTITY_DEPENDENCY_GRAPH` -- never implement standalone graph traversal

**Anti-Patterns:**

- Do NOT implement per-entity impact traversal logic -- use the shared dependency graph
- Do NOT add metrics definitions outside of `metrics.py` files
- Do NOT add health checks to liveness probes -- liveness must be dependency-free
- Do NOT apply version prefixes in individual router files -- the top-level router owns versioning
- Do NOT implement RFC 6902 parsing per-entity -- use the shared `apply_json_patch` function
- Do NOT serialize dump entities using domain models -- use Pydantic router models (API contract)
- Do NOT restructure authorization-api into directories during Phase 1 -- add new files at the package level
- Do NOT implement RFC 6902 parsing from scratch -- use the `jsonpatch` library (python-json-patch)

## Project Structure & Boundaries

### Existing Monorepo Structure

Guardian is a monorepo with 5 source components, OPA configuration, Keycloak provisioning, App Center packaging, and documentation:

```
guardian/
├── management-api/                    # Python/FastAPI -- CRUD for Guardian entities
│   ├── guardian_management_api/
│   │   ├── main.py                    # FastAPI app entrypoint
│   │   ├── business_logic.py          # Hexagonal center -- all business logic
│   │   ├── adapter_registry.py        # port-loader adapter registration
│   │   ├── constants.py
│   │   ├── correlation_id.py
│   │   ├── errors.py
│   │   ├── logging.py
│   │   ├── ports/                     # Abstract port interfaces (ABCs)
│   │   │   ├── base.py, app.py, authz.py, bundle_server.py
│   │   │   ├── capability.py, condition.py, context.py
│   │   │   ├── namespace.py, permission.py, role.py
│   │   ├── adapters/                  # Concrete adapter implementations
│   │   │   ├── app.py, authz.py, bundle_server.py
│   │   │   ├── capability.py, condition.py, context.py
│   │   │   ├── namespace.py, permission.py, role.py
│   │   │   ├── sql_persistence.py, fastapi_utils.py
│   │   ├── models/                    # Domain + DB models
│   │   │   ├── base.py, app.py, authz.py, capability.py
│   │   │   ├── condition.py, context.py, namespace.py
│   │   │   ├── permission.py, role.py, sql_persistence.py
│   │   │   └── routers/              # Pydantic request/response models
│   │   │       ├── base.py, app.py, capability.py, condition.py
│   │   │       ├── context.py, custom_endpoint.py
│   │   │       ├── namespace.py, permission.py, role.py
│   │   └── routers/                   # FastAPI route handlers
│   │       ├── app.py, capability.py, condition.py, context.py
│   │       ├── custom_endpoint.py, namespace.py
│   │       ├── permission.py, role.py
│   ├── alembic/                       # Database migrations
│   │   ├── versions/                  # 3 migration files (1.0.0, 2.0.0, 3.0.4)
│   │   ├── 1.0.0_builtin_conditions/ # 12 stock conditions (Rego + JSON + tests)
│   │   └── 3.0.4_builtin_conditions/ # 1 additional condition
│   ├── rego_policy_bundle_template/   # OPA bundle template (base Rego + test data)
│   ├── tests/                         # pytest suite
│   │   ├── conftest.py
│   │   ├── test_business_logic.py, test_main.py, ...
│   │   ├── adapters/                  # Adapter tests (1 file per adapter)
│   │   ├── models/                    # Model tests
│   │   └── routes/                    # Route tests (1 file per entity)
│   ├── pyproject.toml, poetry.lock, alembic.ini, Dockerfile
│
├── authorization-api/                 # Python/FastAPI -- Permission checks
│   ├── guardian_authorization_api/    # NOTE: Flat file structure, not directories
│   │   ├── main.py, business_logic.py, adapter_registry.py
│   │   ├── constants.py, correlation_id.py, errors.py, logging.py
│   │   ├── ports.py                   # All ports in single file
│   │   ├── routes.py                  # All routes in single file
│   │   ├── udm_client.py             # UDM REST API client for lookups
│   │   ├── adapters/                  # api.py, persistence.py, policies.py
│   │   └── models/                    # opa.py, persistence.py, policies.py, routes.py
│   ├── tests/
│   │   ├── conftest.py, mock_classes.py
│   │   ├── adapters/                  # test_api.py, test_persistence.py, test_policies.py
│   │   └── routes/                    # test_get_permissions.py, test_permissions_check.py
│   ├── pyproject.toml, poetry.lock, Dockerfile
│
├── guardian-lib/                       # Shared Python library
│   ├── guardian_lib/
│   │   ├── adapter_registry.py, logging.py, ports.py
│   │   ├── adapters/                  # authentication.py, settings.py
│   │   └── models/                    # authentication.py
│   ├── guardian_pytest/               # Pytest plugin / test utilities
│   ├── tests/
│   ├── pyproject.toml, poetry.lock
│
├── authorization-client/              # Sync Python HTTP client library
│   ├── guardian_authorization_client/
│   │   ├── authorization.py, config.py, management.py
│   ├── pyproject.toml, poetry.lock    # NOTE: no tests/ directory (must be created)
│
├── management-ui/                     # Vue 3 Composition API frontend
│   ├── src/
│   │   ├── App.vue, main.ts
│   │   ├── ports/                     # authentication.ts, data.ts, settings.ts
│   │   ├── adapters/                  # authentication.ts, data.ts, errors.ts, settings.ts
│   │   ├── stores/                    # adapter.ts, error.ts, settings.ts (Pinia)
│   │   ├── router/                    # index.ts
│   │   ├── views/                     # EditView.vue, ListView.vue, PageNotFound.vue
│   │   ├── helpers/
│   │   │   ├── cookies.ts, dataAccess.ts, validators.ts
│   │   │   ├── configs/              # View configuration definitions
│   │   │   ├── models/               # TypeScript domain models per entity
│   │   │   └── mocks/                # Mock data for testing
│   │   ├── i18n/                      # de.json, en.json + VEB overwrites
│   │   ├── assets/                    # style.styl
│   │   └── tests/                     # Unit test components / fixtures
│   ├── e2e/                           # Playwright E2E tests
│   ├── package.json, yarn.lock, vite.config.ts, vitest.config.ts
│   ├── playwright.config.ts, eslint.config.js, tsconfig*.json
│   └── docker/                        # Dockerfile, nginx.conf
│
├── opa/                               # OPA configuration
│   ├── Dockerfile, opa_config.yaml
│
├── keycloak/                          # Keycloak provisioning
│   ├── Dockerfile
│   └── provisioning/                  # configure.py, client configs
│
├── appcenter-authz/                   # App Center packaging (authorization-api)
├── appcenter-management/              # App Center packaging (management-api)
├── appcenter-management-ui/           # App Center packaging (management-ui)
├── appcenter-common/                  # Shared App Center templates
│
├── docs/                              # Project documentation
│   ├── devel/                         # Concept proposal, integration guide, port reference
│   ├── architecture-documentation/    # Sphinx: architecture docs
│   ├── developer-reference/           # Sphinx: developer reference
│   └── guardian-manual/               # Sphinx: user manual
│
├── dev-compose.yaml                   # Docker Compose for development
├── dev-compose-postgres.yaml          # Docker Compose with PostgreSQL
├── .pre-commit-config.yaml            # Pre-commit hooks
├── .gitlab-ci.yml                     # CI/CD pipeline
└── AGENTS.md                          # AI agent instructions
```

### New Files & Directories Introduced by Phase 1 Decisions

```
guardian/
├── management-api/
│   ├── guardian_management_api/
│   │   ├── metrics.py                       # NEW: Prometheus metric definitions (Pattern 6)
│   │   ├── ports/
│   │   │   └── bundle_auth.py               # NEW: BundleAuthenticationPort (Decision 5, Pattern 4)
│   │   ├── adapters/
│   │   │   └── bundle_auth.py               # NEW: BearerTokenBundleAuthenticationAdapter
│   │   ├── models/
│   │   │   └── routers/
│   │   │       ├── admin.py                 # NEW: Dump/restore Pydantic models (Decision 6)
│   │   │       ├── impact.py                # NEW: Impact preview response models (Decision 2)
│   │   │       └── permissions.py           # NEW: Permission trace models (Decision 4)
│   │   └── routers/
│   │       ├── admin.py                     # NEW: /v1/dump, /v1/restore (Pattern 2)
│   │       ├── operations.py                # NEW: /healthz, /readyz, /startupz, /metrics (Pattern 2)
│   │       └── permissions.py               # NEW: /v1/permissions/trace (Pattern 2)
│   ├── alembic/
│   │   └── versions/
│   │       └── 4.0.0_multi_role_capability.py  # NEW: M2M join table migration (Decision 1)
│   ├── tests/
│   │   └── routes/
│   │       └── test_admin.py                # NEW: dump/restore integration tests
│
├── authorization-api/
│   ├── guardian_authorization_api/          # Retains flat structure -- no directory restructuring
│   │   ├── metrics.py                       # NEW: Prometheus metric definitions (Pattern 6)
│   │   └── operations.py                    # NEW: Health probes + metrics mount
│
├── guardian-lib/
│   ├── guardian_lib/
│   │   └── json_patch.py                    # NEW: Generic apply_json_patch() (Pattern 1)
│   ├── pyproject.toml                       # MODIFIED: add jsonpatch (python-json-patch) dependency
│
├── authorization-client/
│   ├── tests/                               # NEW: test directory (currently missing)
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_management.py               # NEW: tests for multi-role capability support
│
├── management-ui/
│   ├── src/
│   │   ├── components/                      # NEW: Guardian-specific reusable components (Grd prefix)
│   │   │   ├── GrdEntityTree.vue
│   │   │   ├── GrdSplitLayout.vue
│   │   │   ├── GrdConditionBuilder.vue
│   │   │   ├── GrdNamespacedIdentifier.vue
│   │   │   ├── GrdImpactPreview.vue
│   │   │   └── ...
│   │   └── views/
│   │       ├── CapabilityEditor.vue         # NEW: replaces EditView for capabilities
│   │       └── PermissionTraceView.vue      # NEW: per-user permission chain
│
├── guardian-cli/                             # NEW COMPONENT (Decision 6)
│   ├── pyproject.toml
│   ├── guardian_cli/
│   │   ├── __init__.py
│   │   ├── main.py                          # typer app entrypoint
│   │   ├── commands/
│   │   │   ├── dump.py
│   │   │   └── restore.py
│   │   └── client.py                        # httpx client for Management API
│   └── tests/
│       ├── conftest.py
│       ├── test_dump.py
│       └── test_restore.py
│
├── .gitlab-ci.yml                           # MODIFIED: add PII leak detection CI job (NFR28)
```

**Structural decisions:**

- **Authorization API retains its flat file structure in Phase 1.** New files (`metrics.py`, `operations.py`) are added at the package level alongside existing `routes.py` and `ports.py`. No restructuring into directories -- that's a separate cleanup story.
- **`jsonpatch` (python-json-patch)** is added as a new runtime dependency to guardian-lib for RFC 6902 support. This is the second runtime dependency after `loguru` and `port-loader`.
- **Frontend components use `Grd` prefix** (e.g., `GrdEntityTree.vue`) to distinguish Guardian-specific components from VEB library components (`U` prefix). Reusable components go in `src/components/`, page-level views go in `src/views/`.
- **`authorization-client/tests/`** must be created as Phase 1 prerequisite -- FR40-FR41 modifies `management.py` and requires test coverage.
- **PII leak detection** is a CI pipeline job in `.gitlab-ci.yml`, not a test file. It scans log output and test assertions for PII field names above TRACE level.

### Frontend Component Naming Convention

| Prefix | Location | Purpose | Example |
|---|---|---|---|
| `U` | univention-veb library | Shared VEB atoms/molecules | `UButton`, `UComboBox`, `UFormElement` |
| `Grd` | `management-ui/src/components/` | Guardian-specific reusable components | `GrdEntityTree`, `GrdConditionBuilder` |
| None | `management-ui/src/views/` | Page-level views (not reusable) | `CapabilityEditor`, `PermissionTraceView` |

### Architectural Boundaries

**Service Boundaries:**

| Component | Boundary | Communicates With |
|---|---|---|
| Management API | CRUD + admin + policy bundle generation | PostgreSQL (DB), OPA (bundle polling), Keycloak (OIDC validation) |
| Authorization API | Permission check + grant queries | OPA (policy evaluation), UDM REST API (actor/target lookup), Keycloak (OIDC validation) |
| Management UI | Browser SPA | Management API (REST), Keycloak (OIDC login) |
| guardian-lib | Shared library, no runtime boundary | Imported by Management API + Authorization API |
| authorization-client | Sync HTTP client library | Authorization API (REST) |
| guardian-cli (NEW) | Standalone CLI tool | Management API (REST, /v1/dump + /v1/restore) |
| OPA | Policy evaluation sidecar | Management API (bundle polling), Authorization API (query evaluation) |

**Data Boundaries:**

| Data Store | Owner | Consumers | Access Pattern |
|---|---|---|---|
| PostgreSQL | Management API (sole writer) | Management API only | SQLAlchemy async ORM via Alembic-managed schema |
| OPA Bundle Cache | OPA (local cache) | Authorization API (query), OPA (evaluation) | Periodically pulled from Management API bundle endpoint |
| UDM/LDAP | External (UCS Directory Manager) | Authorization API (read-only via UDM REST API) | HTTP GET for actor/target attribute lookup |
| Keycloak | External (Identity Provider) | Management API, Management UI (OIDC token validation) | JWT token validation, no direct DB access |

**Port/Adapter Boundary Rules:**

- Business logic (`business_logic.py`) depends ONLY on port interfaces (ABCs), never on adapters
- Adapters are registered via Poetry entry points and selected by environment variable
- New functionality follows the same pattern: define port, implement adapter, register entry point
- The `ENTITY_DEPENDENCY_GRAPH` in `business_logic.py` is the single source of truth for entity relationships (Pattern 3)

### Requirements to Structure Mapping

**FR1-FR6 (DELETE with referential integrity):**
- Business logic: `management-api/guardian_management_api/business_logic.py` (ENTITY_DEPENDENCY_GRAPH + traversal function)
- Impact preview routes: each entity router file in `routers/` (sub-resource pattern)
- Impact models: `models/routers/impact.py`
- Tests: `tests/routes/test_*.py` (one per entity, extend with DELETE + impact tests)

**FR7-FR10 (Multi-role capabilities):**
- Schema migration: `alembic/versions/4.0.0_multi_role_capability.py`
- Domain model: `models/capability.py` (Capability.roles: list[Role])
- Router model: `models/routers/capability.py` (update request/response)
- SQL model: `models/sql_persistence.py` (new capability_role table)
- Persistence adapter: `adapters/capability.py`
- OPA bundle: `adapters/bundle_server.py` (roleCapabilityMapping generation)
- JSON PATCH: `guardian-lib/guardian_lib/json_patch.py`

**FR11-FR15 (Authorization decisions):**
- No structural changes -- existing Authorization API endpoints and adapters
- Performance validation via new `authorization-api/guardian_authorization_api/metrics.py`

**FR16-FR19 (Permission reporting):**
- New endpoint: `management-api/guardian_management_api/routers/permissions.py`
- Models: `models/routers/permissions.py`
- Business logic: new function in `business_logic.py`
- UI: `management-ui/src/views/PermissionTraceView.vue`

**FR20-FR26 (Logging & observability):**
- Logging: existing `logging.py` in each service (minimal changes)
- Correlation ID: `correlation_id.py` in each service (sanitization fix)
- Health probes: `routers/operations.py` (Management API), `operations.py` (Authorization API)
- Metrics: `metrics.py` in each service + operations routes
- PII detection: `.gitlab-ci.yml` (new CI pipeline job)

**FR27-FR31 (Configuration & deployment):**
- DB URI: `adapters/sql_persistence.py` configuration
- Bundle auth: `ports/bundle_auth.py` + `adapters/bundle_auth.py`
- OIDC fix: `guardian-lib/guardian_lib/adapters/authentication.py`
- API versioning: `main.py` (router mounting with prefix)
- App Center: `appcenter-*/settings` files
- OPA config: `opa/opa_config.yaml` (bearer token)

**FR32-FR34 (CLI tool):**
- New component: `guardian-cli/` (entire directory)
- Management API endpoints: `routers/admin.py` + `models/routers/admin.py`
- Integration tests: `tests/routes/test_admin.py`

**FR35-FR39 (Management UI):**
- New components: `management-ui/src/components/` (Grd-prefixed reusable components)
- New views: `management-ui/src/views/` (CapabilityEditor, PermissionTraceView)
- Updated adapters: `management-ui/src/adapters/data.ts` (new API endpoints)
- Updated stores: `management-ui/src/stores/` (new entity stores as needed)
- Updated i18n: `management-ui/src/i18n/locales/` (new translation keys)

**FR40-FR41 (Authorization client):**
- `authorization-client/guardian_authorization_client/management.py` (multi-role capability support)
- `authorization-client/tests/test_management.py` (new test file)

**FR42-FR46 (Documentation deliverables):**
- Integration Guide: `docs/developer-reference/` (new .rst file in existing Sphinx doc set)
- Support Handbook: `docs/developer-reference/` (new .rst file)
- Administrator Guide: `docs/guardian-manual/` (new .rst file in existing Sphinx doc set)
- Operations Guide: `docs/guardian-manual/` (new .rst file)

### Integration Points

**Internal Communication:**

```
Management UI ──HTTP/REST──> Management API ──SQLAlchemy──> PostgreSQL
                                    │
                                    ├──bundle polling──> OPA
                                    │
guardian-cli ───HTTP/REST──> Management API

Authorization API ──HTTP──> OPA (policy query)
       │
       └──HTTP──> UDM REST API (actor/target lookup)
```

**External Integrations:**

| External System | Protocol | Guardian Component | Purpose |
|---|---|---|---|
| Keycloak | OIDC / OAuth 2.0 | Management API, Management UI | Authentication |
| UDM REST API | HTTP REST | Authorization API | Actor/target attribute lookup |
| PostgreSQL | TCP (asyncpg) | Management API | Entity persistence |
| OPA | HTTP REST (bundle + query) | Management API (bundle), Authorization API (query) | Policy distribution + evaluation |

**Data Flow for Authorization Check:**

1. Caller -> Authorization API: "Does actor X have permissions P on target T?"
2. Authorization API -> UDM REST API: Fetch actor attributes and roles (if "with-lookup" variant)
3. Authorization API -> OPA: Query policy with actor, target, permissions
4. OPA evaluates Rego policies against cached bundle data
5. OPA -> Authorization API: Permission result
6. Authorization API -> Caller: Yes/no or permission list

**Data Flow for Configuration Change:**

1. Admin -> Management UI -> Management API: Create/update/delete entity
2. Management API -> PostgreSQL: Persist change
3. Management API: Regenerate OPA bundle asynchronously (<30s)
4. OPA polls bundle endpoint (10-15s interval): Fetches new bundle
5. OPA caches new policies: Next authorization check uses updated rules

## Architecture Validation Results

### Coherence Validation

**Decision Compatibility:** All 10 decisions are compatible with each other and with the existing technology stack. No version conflicts introduced. The dependency ordering (data model -> API surface -> UI/tooling -> infrastructure) is internally consistent. Cross-decision dependencies are documented and resolvable.

**Pattern Consistency:** All 8 implementation patterns follow the established hexagonal architecture. Naming conventions are consistent with the 127 rules in project-context.md. No contradictions between patterns and decisions.

**Structure Alignment:** New files and directories follow the existing component conventions in each service. The authorization-api's flat file structure is preserved. The management-api's directory-based structure is extended consistently. Frontend component naming (Grd prefix) is distinct from VEB (U prefix).

**Minor note:** `jsonpatch` becomes a transitive dependency of Authorization API via guardian-lib, though Authorization API doesn't use JSON PATCH. This is acceptable given the library's minimal footprint.

### Requirements Coverage Validation

**Functional Requirements:** All 46 FRs (FR1-FR46) are architecturally supported and mapped to specific file locations in the project structure. No orphaned requirements.

**Non-Functional Requirements:** All 28 NFRs are addressed:
- Performance targets have metrics infrastructure (Decision 10) with custom histogram buckets tuned to each target
- Security requirements are covered by Decisions 3 (versioning), 5 (bundle auth), 8 (PII)
- Scalability is preserved by maintaining stateless component design
- Reliability is supported by Decision 9 (probes) and existing OPA caching architecture
- Test quality requirements are mapped to test directories and CI pipeline additions

### Implementation Readiness Validation

**Decision Completeness:** 10 decisions documented with category, rationale, affected components, and specific technical choices. All new dependencies identified (typer, httpx, jsonpatch, prometheus-client).

**Structure Completeness:** Every new file has a specific path. Every FR is mapped to exact directories. New component (guardian-cli) has full directory layout defined.

**Pattern Completeness:** 8 patterns covering all identified conflict points. Enforcement guidelines and anti-patterns documented.

### Gap Analysis Results

**No critical gaps found.**

**Important gaps (addressable during story creation):**

1. RFC 6902 PATCH Phase 1 scope: recommend capabilities only, other entities in subsequent phases
2. Restore endpoint conflict resolution strategy (fail/skip/overwrite): defer to story definition
3. Management UI state management for new views: defer to implementation
4. FastAPI version harmonization: recommend as Phase 1 prerequisite story

**Nice-to-have gaps (defer to implementation):**

5. Shared error code registry for new endpoints
6. Pagination pattern for impact preview and permission trace (not needed at current scale)

### Architecture Completeness Checklist

**Requirements Analysis**

- [x] Project context thoroughly analyzed (46 FRs, 28 NFRs, 10 categories)
- [x] Scale and complexity assessed (High / Enterprise)
- [x] Technical constraints identified (8 hard constraints, 4 external dependencies)
- [x] Cross-cutting concerns mapped (7 concerns)
- [x] Stakeholder impact mapped to Phase 1 requirements
- [x] Architectural decision dependency ordering established

**Architectural Decisions**

- [x] 6 critical decisions documented (multi-role, DELETE, versioning, trace, bundle auth, CLI)
- [x] 4 important decisions documented (impact preview, logging, probes, metrics)
- [x] 4 decisions explicitly deferred with rationale
- [x] Technology stack fully specified (locked-in vs. evolutionary)
- [x] New dependencies identified (typer, httpx, jsonpatch, prometheus-client)

**Implementation Patterns**

- [x] 8 conflict points identified and resolved
- [x] Naming conventions established (Grd prefix for frontend components)
- [x] Structure patterns defined (endpoint organization, flat vs. directory)
- [x] Process patterns documented (graph traversal, content-type discrimination, probe response format)
- [x] Anti-patterns listed

**Project Structure**

- [x] Complete existing directory structure documented
- [x] All new files and directories mapped with rationale
- [x] Component boundaries established (service, data, port/adapter)
- [x] Requirements to structure mapping complete (all 46 FRs)
- [x] Integration points and data flows documented

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High

**Key Strengths:**

- Builds on a well-established hexagonal architecture with 127 existing rules
- All decisions minimize disruption to existing consumers (alias versioning, backward-compatible migrations)
- Clear dependency ordering prevents implementation sequencing errors
- Every decision has explicit rationale tied to requirements
- Brownfield-aware -- distinguishes locked-in decisions from evolutionary opportunities

**Areas for Future Enhancement:**

- Runtime decision trace (OPA decision logging) -- Phase 2/3
- Cerbos evaluation as alternative policy engine -- Phase 3
- authorization-client async variant -- as needed
- Authorization API directory restructuring -- dedicated cleanup story
- FastAPI version pin harmonization -- Phase 1 prerequisite
- guardian-lib async adapter migration -- directional intent, incremental

### Implementation Handoff

**AI Agent Guidelines:**

- Follow all architectural decisions exactly as documented in this file
- Follow the 127 rules in `project-context.md` for code style, naming, and quality
- Follow the 8 implementation patterns for all new Phase 1 functionality
- Respect the project structure and file placement conventions
- Use the `ENTITY_DEPENDENCY_GRAPH` for all dependency traversal -- never implement standalone
- When in doubt, check existing code in the same component for precedent

**First Implementation Priority (dependency order):**

1. Alembic migration for multi-role capability join table (Decision 1)
2. Domain model + router model + SQL model updates for `Capability.roles`
3. API versioning middleware (Decision 3) -- affects all subsequent endpoint work
4. DELETE with referential integrity + impact preview (Decisions 2, 7)
5. Permission trace endpoint (Decision 4)
6. Bundle endpoint bearer token auth (Decision 5)
7. CLI dump/restore (Decision 6) -- depends on versioned endpoints
8. Management UI components (FR35-FR39) -- depends on all API changes
9. Health probes + metrics (Decisions 9, 10) -- independent, can parallel with other work
10. Logging fixes (Decision 8) -- independent, can parallel
