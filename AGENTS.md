# AGENTS.md -- Guardian

> **Detailed rules and conventions are in
> [`_bmad-output/project-context.md`](_bmad-output/project-context.md).**
> Read that file before implementing any code. This file provides the project
> overview, directory map, architecture invariants, and quick-reference commands
> only.
>
> **Phase 1 architectural decisions, implementation patterns, new file layout,
> and anti-patterns are in
> [`_bmad-output/planning-artifacts/architecture.md`](_bmad-output/planning-artifacts/architecture.md).**
> Consult that file when implementing any Phase 1 feature.

## Project Overview

Guardian is an **Attribute-Based Access Control (ABAC) authorization engine** for
Univention Corporate Server (UCS). It acts as a **policy decision point (PDP)** --
applications remain the **policy enforcement point (PEP)** and must enforce
decisions themselves. OPA (Open Policy Agent) with Rego policies handles
evaluation.

- **Language:** Python 3.11+ (backend), TypeScript (frontend)
- **License:** AGPL-3.0-only (REUSE-compliant -- every source file needs an SPDX header)
- **Package managers:** Poetry (Python), Yarn 1.22.x (frontend)

For full technology stack, component diagrams, and data flows see
[`docs/project-overview.md`](docs/project-overview.md) and
[`docs/integration-architecture.md`](docs/integration-architecture.md).

For the complete domain model (actors, roles, permissions, capabilities,
conditions, namespaces, contexts) see
[`docs/devel/concept_proposal.md`](docs/devel/concept_proposal.md).

**Terminology note:** The term **capability** is deprecated and will be replaced
by **privilege** in a future refactoring. The codebase, API endpoints, database
schema, and concept proposal document still use "capability" throughout. Until
the rename is applied, use "capability" in code to match the existing codebase.
In new documentation, prefer "privilege". The two terms are synonymous.

## Project Structure

```text
guardian/
├── management-api/                    # Python/FastAPI -- CRUD for ABAC entities + OPA bundle server
│   ├── guardian_management_api/
│   │   ├── main.py                    # FastAPI app entrypoint
│   │   ├── business_logic.py          # Hexagonal center -- all business logic (1746 lines)
│   │   ├── adapter_registry.py        # port-loader adapter registration
│   │   ├── constants.py, correlation_id.py, errors.py, logging.py
│   │   ├── models/                    # Domain models (@dataclass) + SQL models (SQLAlchemy)
│   │   │   ├── base.py, app.py, namespace.py, role.py, permission.py
│   │   │   ├── condition.py, capability.py, context.py, authz.py
│   │   │   ├── sql_persistence.py     # SQLAlchemy ORM schema (10 tables)
│   │   │   └── routers/              # Pydantic request/response models
│   │   ├── ports/                     # Abstract port interfaces (ABCs)
│   │   ├── adapters/                  # Concrete adapter implementations
│   │   └── routers/                   # FastAPI route handlers (thin wrappers)
│   ├── alembic/                       # Database migrations (3 versions: 1.0.0, 2.0.0, 3.0.4)
│   ├── rego_policy_bundle_template/   # OPA Rego policy source
│   ├── tests/                         # pytest suite (mirrors source structure)
│   └── pyproject.toml
│
├── authorization-api/                 # Python/FastAPI -- Permission checks
│   ├── guardian_authorization_api/    # NOTE: Flat file structure, not directories
│   │   ├── main.py, business_logic.py, adapter_registry.py
│   │   ├── ports.py                   # All ports in single file
│   │   ├── routes.py                  # All routes in single file (5 endpoints)
│   │   ├── udm_client.py             # Vendored UDM REST API client (801 lines)
│   │   ├── adapters/                  # api.py, persistence.py, policies.py
│   │   └── models/                    # opa.py, persistence.py, policies.py, routes.py
│   ├── tests/
│   └── pyproject.toml
│
├── guardian-lib/                       # Shared Python library (port-loader, auth, settings, logging)
│   ├── guardian_lib/
│   │   ├── ports.py, adapter_registry.py, logging.py
│   │   ├── adapters/                  # authentication.py, settings.py
│   │   └── models/
│   ├── guardian_pytest/               # Shared test fixtures (RSA keys, mock JWKS, token fixtures)
│   ├── tests/
│   └── pyproject.toml
│
├── authorization-client/              # Sync Python HTTP client library (requests, no async)
│   ├── guardian_authorization_client/
│   │   ├── authorization.py           # Remote + local authorization clients
│   │   ├── management.py             # Remote + local management clients
│   │   └── config.py
│   └── pyproject.toml                 # NOTE: no tests/ directory (must be created for Phase 1)
│
├── management-ui/                     # Vue 3 Composition API frontend
│   ├── src/
│   │   ├── App.vue, main.ts
│   │   ├── ports/                     # TypeScript port interfaces
│   │   ├── adapters/                  # authentication.ts, data.ts (1805 lines), settings.ts
│   │   ├── stores/                    # Pinia stores: adapter.ts, error.ts, settings.ts
│   │   ├── views/                     # ListView.vue, EditView.vue, PageNotFound.vue
│   │   ├── router/                    # Vue Router (14 production + 5 test routes)
│   │   ├── helpers/                   # dataAccess.ts, validators.ts, models/, configs/, mocks/
│   │   └── i18n/                      # en.json, de.json (181 keys each)
│   ├── e2e/                           # Playwright E2E tests
│   └── package.json, vite.config.ts
│
├── opa/                               # OPA container config + opa_config.yaml
├── keycloak/                          # Keycloak provisioning (configure.py + client configs)
│
├── appcenter-authz/                   # UCS App Center packaging (authorization-api)
├── appcenter-management/              # UCS App Center packaging (management-api)
├── appcenter-management-ui/           # UCS App Center packaging (management-ui)
├── appcenter-common/                  # Shared App Center resources
│
├── docs/                              # Generated + manual documentation (see index.md)
│   ├── devel/                         # Concept proposal, integration guide, port reference
│   ├── architecture-documentation/    # Sphinx architecture docs
│   ├── developer-reference/           # Sphinx developer reference
│   └── guardian-manual/               # Sphinx user manual
│
├── _bmad-output/                      # BMAD planning artifacts
│   ├── project-context.md             # 127 AI-optimized rules for code generation
│   └── planning-artifacts/            # PRD, architecture decisions, UX spec
│
├── dev-compose.yaml                   # Docker Compose for local development (8 services)
├── dev-compose-postgres.yaml          # PostgreSQL override
├── .pre-commit-config.yaml            # Pre-commit hooks (Black, Ruff, mypy, Bandit)
└── .gitlab-ci.yml                     # CI/CD pipeline
```

For the fully annotated source tree with per-file descriptions, see
[`docs/source-tree-analysis.md`](docs/source-tree-analysis.md).

For new files and directories introduced by Phase 1, see
[`_bmad-output/planning-artifacts/architecture.md` > Project Structure](_bmad-output/planning-artifacts/architecture.md).

## Where to Find What

| Topic | Location |
|-------|----------|
| Technology stack & version pins | [`project-context.md` > Technology Stack](_bmad-output/project-context.md) |
| Import, typing, exception, logging conventions | [`project-context.md` > Language-Specific Rules](_bmad-output/project-context.md) |
| Hexagonal architecture & boundary rules | [`project-context.md` > Framework-Specific Rules](_bmad-output/project-context.md) |
| Testing patterns, fixtures, mocking | [`project-context.md` > Testing Rules](_bmad-output/project-context.md) |
| Formatting, naming, linting, SPDX headers | [`project-context.md` > Code Quality & Style Rules](_bmad-output/project-context.md) |
| CI/CD, release process, dependency management | [`project-context.md` > Development Workflow Rules](_bmad-output/project-context.md) |
| Anti-patterns, edge cases, gotchas | [`project-context.md` > Critical Don't-Miss Rules](_bmad-output/project-context.md) |
| Full domain model (actors, roles, capabilities, ...) | [`docs/devel/concept_proposal.md`](docs/devel/concept_proposal.md) |
| Per-part architecture deep dives | [`docs/architecture-*.md`](docs/) (one per component) |
| API contracts (50+ REST endpoints) | [`docs/api-contracts-*.md`](docs/) |
| Data models & SQL schema | [`docs/data-models-*.md`](docs/) |
| Integration architecture & data flows | [`docs/integration-architecture.md`](docs/integration-architecture.md) |
| Environment variables (all services) | [`docs/development-guide.md` > Environment Variables](docs/development-guide.md) |
| Phase 1 architectural decisions (10) | [`architecture.md` > Core Decisions](_bmad-output/planning-artifacts/architecture.md) |
| Phase 1 implementation patterns (8) | [`architecture.md` > Implementation Patterns](_bmad-output/planning-artifacts/architecture.md) |
| Phase 1 new files & directory layout | [`architecture.md` > Project Structure](_bmad-output/planning-artifacts/architecture.md) |
| Phase 1 product requirements | [`_bmad-output/planning-artifacts/prd.md`](_bmad-output/planning-artifacts/prd.md) |
| Phase 1 UX design specification | [`_bmad-output/planning-artifacts/ux-design-specification.md`](_bmad-output/planning-artifacts/ux-design-specification.md) |
| Full documentation index | [`docs/index.md`](docs/index.md) |

## Architecture

**IMPORTANT:** All code changes must adhere to the **hexagonal / ports and
adapters architecture**. Business logic must depend only on abstract port
interfaces, never on concrete adapter implementations. New functionality should
be added by implementing new adapters behind existing ports or by defining new
ports where needed. Do not bypass the port layer by calling adapters directly
from business logic or routes.

Flow: **Router -> Business Logic -> Ports (abstract) -> Adapters (concrete).**

The codebase enforces three separate model layers -- domain `@dataclass` classes,
Pydantic router models, and SQLAlchemy DB models (management-api only). Adapters
translate between these layers; they are never the same classes.

Backend adapters are registered via Python entry points (`port-loader` library)
in `pyproject.toml` and selected at runtime through
`GUARDIAN__<SERVICE>__ADAPTER__<PORT_NAME>` environment variables. Frontend
adapters are selected via Pinia adapter store with switch/case on configuration
strings.

For per-component architecture details, see `docs/architecture-*.md`. For the
full set of Phase 1 architectural decisions (10 decisions), implementation
patterns (8 patterns), new file/directory layout, and anti-patterns, see
[`_bmad-output/planning-artifacts/architecture.md`](_bmad-output/planning-artifacts/architecture.md).

## Code Style

Authoritative formatting is enforced by pre-commit hooks (Black, Ruff, mypy,
Bandit, ESLint, Prettier, vue-tsc). The rules below capture conventions that are
**not** machine-enforced. For the full set of 127 rules, see
[`_bmad-output/project-context.md`](_bmad-output/project-context.md).

### File Header (Required on Every Source File)

```python
# Copyright (C) 2026 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
```

### Python

- **Logging:** `loguru` only -- never `import logging`
- **String formatting:** f-strings only (no `.format()` or `%`)
- **Empty bodies:** `...` (ellipsis), not `pass`
- **Async everywhere:** All persistence and business logic functions are `async`.
  **Exception:** `authorization-client` is synchronous (`requests`, no async).
- **Relative imports** within the same service package; absolute imports for
  cross-package references (e.g., `from guardian_lib.ports import SettingsPort`)
- **Pydantic v2 only:** `model_config = ConfigDict(...)`, `.model_dump()`,
  `.model_validate()`. **Note:** port-loader adapters use a separate
  `class Config` with `alias` -- this is port-loader's mechanism, not Pydantic.
  Do not "fix" adapter `class Config` blocks.
- **Domain models are `@dataclass`**, not Pydantic models. Frozen dataclasses
  for query objects (`@dataclass(frozen=True)`).
- **Type hints are mandatory.** Use `X | None` (Python 3.11+ syntax). Do NOT add
  `from __future__ import annotations`.

### TypeScript / Vue

- **Composition API only** with `<script setup lang="ts">` -- never Options API
- **i18next** for all user-facing strings -- never hardcode display text
- **`@univention/univention-veb`** component library for all UI atoms
- **Unused variables** must be prefixed with `_` (ESLint enforces this)
- **Known typo:** Frontend route path for capabilities is misspelled as
  `capabilties` (missing 'i'). Do NOT fix without a migration plan.

### Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Port classes | `PascalCase` + `Port` suffix | `RolePersistencePort` |
| Adapter classes | Technology prefix + `PascalCase` | `SQLRolePersistenceAdapter` |
| DB models | `DB` prefix | `DBRole`, `DBNamespace` |
| Domain models | Plain `PascalCase` dataclass | `Role`, `RoleGetQuery` |
| Router models | Action suffix | `RoleCreateRequest`, `RoleSingleResponse` |
| Env variables | `GUARDIAN__<SERVICE>__<SECTION>__<KEY>` | `GUARDIAN__MANAGEMENT__ADAPTER__SETTINGS_PORT` |
| Vue components | `PascalCase.vue` | `ListView.vue` |
| Pinia stores | `use<Name>Store` | `useErrorStore` |

Full naming table in [`project-context.md` > Code Quality & Style Rules](_bmad-output/project-context.md).

## Critical Rules (Do NOT Violate)

- **No business logic in routers or adapters** -- all logic in `business_logic.py`
- **No shared model classes across layers** -- domain dataclasses, Pydantic
  router models, and SQLAlchemy DB models are always separate
- **No Pydantic v1 patterns** -- no `.dict()`, `.parse_obj()`, inner `class Config`
- **No stdlib `logging`** -- always `loguru`
- **No `PUT` for updates** -- always `PATCH`. **Exception: capability uses `PUT`**
  (full replacement semantics)
- **No catching domain errors in routers** -- errors flow through
  `TransformExceptionMixin` in the API adapter
- **No `asyncio.create_subprocess_shell` with f-strings** -- use
  `create_subprocess_exec` with explicit arguments
- **No synchronous `requests` in `async def`** -- use `httpx.AsyncClient`
- **No `assert` for validation in production code** -- use explicit `if`/`raise`
- **`@pytest.mark.asyncio` on every async test** -- `asyncio_mode = "auto"` is
  NOT configured; without the decorator, async tests silently pass without
  executing
- **Every adapter loadable via entry points must have** `class Config` with
  `alias` -- forgetting it breaks the plugin system silently
- **Always validate with `pre-commit run --all-files`** before considering work
  complete

Full anti-patterns, edge cases, and gotchas in
[`project-context.md` > Critical Don't-Miss Rules](_bmad-output/project-context.md).

## Quick Reference: Commands

### Install Dependencies

```bash
# Python (from within a subproject directory)
poetry install

# Frontend
cd management-ui && yarn install
```

### Running Tests

```bash
# Management API (no external services required for unit tests)
poetry run pytest tests/                         # all tests
poetry run pytest tests/test_business_logic.py   # single file
poetry run pytest tests/routes/test_app.py::TestAppEndpoints::test_post_app_minimal
poetry run pytest -k "test_post_app"             # by name pattern
poetry run pytest -m "not e2e"                   # skip e2e tests

# Inside Docker dev container
docker exec management-guardian-dev pytest -v /app/management-api/tests/

# Authorization API (integration tests require OPA with test data)
docker exec authz-guardian-dev pytest -v /app/authorization-api/tests/

# Management UI
yarn test:unit                           # Vitest (watch mode)
yarn test:unit --run                     # single run, no watch
CI=1 yarn test:e2e --project=chromium    # Playwright E2E (headless)
CI=1 yarn test:e2e                       # all browsers
```

### Linting & Formatting

**IMPORTANT:** After changing any file, ALWAYS run `pre-commit run --all-files`
to execute the pre-commit linters and verify that all checks pass. Fix any
issues reported before proceeding. Do NOT skip this step.

**IMPORTANT:** Black, Ruff, mypy, and Bandit are NOT dev dependencies -- they
exist only in pre-commit's isolated environments. Run them exclusively via
`pre-commit run --all-files`, never install or run them directly.

For the full development setup (Docker Compose, local development, PostgreSQL
mode, CI/CD pipeline, deployment), see
[`docs/development-guide.md`](docs/development-guide.md).
