# AGENTS.md — Guardian

Guardian is an Attribute-Based Access Control (ABAC) authorization engine for
Univention Corporate Server (UCS). It is a monorepo with four main components:
`management-api`, `authorization-api`, `guardian-lib` (shared Python library),
and `management-ui` (Vue 3 frontend). OPA (Open Policy Agent) handles policy
evaluation.

## Purpose and Main Concepts

Guardian is an authorization service (not authentication) for UCS and SWP
applications. It acts as a **policy decision point (PDP)** — applications remain
the **policy enforcement point (PEP)** and must enforce decisions themselves.
Guardian uses OPA (Open Policy Agent) with Rego policies as its evaluation
backend.

Key domain concepts (see `docs/devel/concept_proposal.md` for full details):

**Note:** The term **capability** has been deprecated and replaced by
**privilege** throughout the codebase. The concept proposal document still uses
the old term; in new code and documentation, always use **privilege**.

- **Actor**: An authenticated entity (user, server, machine account) that
  performs actions. Actors are assigned roles.
- **Permission**: An opaque string representing an operation an application
  wants to authorize (e.g., `read_first_name`, `export`). Guardian does not
  know what a permission means — the application defines and enforces that.
- **Target**: The object a permission applies to (e.g., a student LDAP object,
  an API endpoint). Targets are optional in authorization requests.
- **Role**: A string (e.g., `ucsschool:users:teacher`) that maps actors to
  privileges via role-privilege-mappings. Roles are namespaced by app and
  namespace.
- **Context**: An optional tag that restricts a role to a subset of targets
  sharing the same tag (e.g., a school). Primarily used by UCS@school.
- **Privilege**: A combination of permissions and conditions that defines what
  a role is allowed to do. Conditions are boolean Rego functions that further
  constrain when permissions apply.
- **Namespace**: A scoping mechanism (`app-name:namespace-name`) that prevents
  collisions between different applications' roles, permissions, and contexts.
- **Role-Capability-Mapping**: JSON configuration that maps roles to
  privileges. This is what generates OPA policies.
- **Condition**: A boolean Rego function used within privileges to restrict
  permissions based on attributes of the actor, target, or request context
  (e.g., `target_is_self`, `target_has_role`).

The two main API surfaces are:
1. **Authorization API** — answers "does this actor have these permissions?" and
   "what permissions does this actor have for these targets?"
2. **Management API** — CRUD for apps, namespaces, roles, permissions, contexts,
   conditions, and role-privilege-mappings.

## Architecture

**IMPORTANT:** All code changes must adhere to the **hexagonal / ports and
adapters architecture**. Business logic must depend only on abstract port
interfaces, never on concrete adapter implementations. New functionality should
be added by implementing new adapters behind existing ports or by defining new
ports where needed. Do not bypass the port layer by calling adapters directly
from business logic or routes.

The project uses **hexagonal architecture (ports and adapters)** in both backend
and frontend. Ports define abstract interfaces; adapters provide concrete
implementations. Adapters are registered via Python entry points in
`pyproject.toml` and selected at runtime through environment variables.

Flow: Router -> Business Logic -> Ports (abstract) -> Adapters (concrete).
Business logic functions accept port interfaces as parameters, never concrete
adapters.

## Build & Test Commands

### Python (Poetry)

Each Python subproject (`management-api`, `authorization-api`, `guardian-lib`,
`authorization-client`) uses Poetry. Install deps from within a subproject dir:

```bash
poetry install                          # install deps for the subproject
```

### Running Tests

**Management API** (can run directly, no external services required for unit tests):

```bash
# All tests (inside Docker dev environment)
docker exec management-guardian-dev pytest -v /app/management-api/tests/

# Locally, from the management-api directory
poetry run pytest tests/                         # all tests
poetry run pytest tests/test_business_logic.py   # single file
poetry run pytest tests/routes/test_app.py::TestAppEndpoints::test_post_app_minimal  # single test
poetry run pytest -k "test_post_app"             # by name pattern
poetry run pytest -m "not e2e"                   # skip e2e tests
```

**Authorization API** (integration tests require OPA with test data loaded):

```bash
docker exec authz-guardian-dev pytest -v /app/authorization-api/tests/
# Same pytest options as above apply for local runs
```

**Management UI** (frontend):

```bash
cd management-ui
yarn install
yarn test:unit                           # Vitest unit tests (watch mode)
yarn test:unit --run                     # single run, no watch
CI=1 yarn test:e2e --project=chromium    # Playwright E2E (headless)
CI=1 yarn test:e2e                       # all browsers
```

### Linting & Formatting

```bash
pre-commit run --all-files               # run all checks

# Python-specific
black --check .                          # format check (line-length=105)
ruff check . --fix                       # lint + autofix
mypy <subproject-dir>                    # type check

# Frontend (from management-ui/)
yarn lint                                # ESLint --fix --max-warnings=0
yarn format                              # Prettier write
yarn type-check                          # vue-tsc
```

**IMPORTANT:** After changing any file, ALWAYS run `pre-commit run --all-files` to execute the pre-commit linters and verify that all checks pass. Fix any issues reported before proceeding. Do NOT skip this step.

## Code Style — Python

### Formatting

- **Black** formatter, **105-char line length**, target Python 3.11.
- **Ruff** linter with rules: `E` (pycodestyle), `F` (pyflakes), `I` (isort).

### Imports

Sorted by ruff (isort rules). Order: stdlib, third-party, local. Use **relative
imports** for local modules:

```python
import asyncio                                          # stdlib
from fastapi import Depends, FastAPI                    # third-party
from guardian_lib.adapter_registry import ADAPTER_REGISTRY
from .adapter_registry import configure_registry        # local (relative)
from ..models.app import App
```

### Type Annotations

Both `Optional[X]` (older code) and `X | Y` (newer code) coexist. Prefer the
modern `X | Y` syntax for new code. Use `Annotated` for Pydantic field
constraints. Return types should be annotated on public functions.

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Classes | PascalCase | `AppAPIPort`, `FastAPIAppAPIAdapter` |
| Functions/methods | snake_case | `create_app`, `get_permissions` |
| Variables | snake_case | `actor_id`, `persistence_port` |
| Constants | UPPER_SNAKE_CASE | `API_PREFIX`, `STRING_MAX_LENGTH` |
| DB models | `DB` prefix | `DBApp`, `DBNamespace` |
| Private methods | leading underscore | `_app_to_db_app` |
| Adapter classes | `FastAPI{Entity}APIAdapter`, `SQL{Entity}PersistenceAdapter` |

### Docstrings

Sphinx/reStructuredText style on port interfaces and models:

```python
"""
:param name: The name of the object
:raises ObjectNotFoundError: If the object was not found.
:return: The created object
"""
```

### Error Handling

Custom exception classes in `errors.py` (e.g., `ObjectNotFoundError(ValueError)`,
`PersistenceError(RuntimeError)`). Exceptions use `...` (Ellipsis) for empty
bodies. Business logic catches all exceptions and delegates to
`transform_exception()` which maps domain exceptions to `HTTPException`:

```python
try:
    ...  # business logic
except Exception as exc:
    raise (await app_api_port.transform_exception(exc)) from exc
```

Do NOT use FastAPI `@app.exception_handler()` decorators.

### Async

Everything is async. Use `async def` for all ports, adapters, business logic,
and routes. Use `port_dep(PortClass, AdapterClass)` from `guardian_lib` for
FastAPI dependency injection.

### Models

- **Domain models**: Python `@dataclass` classes in `models/` directories.
- **API request/response models**: Pydantic `BaseModel` subclasses with mixin
  composition in `models/routers/`. Inherit from `GuardianBaseModel` which sets
  `populate_by_name=True`.
- **DB models**: SQLAlchemy `DeclarativeBase` with `Mapped[]` type annotations
  and `DB` prefix naming.

### License Headers

Every source file must have (REUSE compliant):

```python
# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
```

## Code Style — Frontend (management-ui)

### Formatting & Linting

- **Prettier**: single quotes, 120-char width, ES5 trailing commas, 2-space
  indent, `bracketSpacing: false`.
- **ESLint**: Vue essential + TypeScript rules. `no-explicit-any` is off.
  Prefix unused variables with underscore (`_`).

### Component Structure

Always use `<script setup lang="ts">` (Composition API). Never Options API.

```vue
<script setup lang="ts">
import {ref} from 'vue';
// ...
</script>
<template>...</template>
<style lang="stylus">...</style>
```

### TypeScript Patterns

- Use `Result<T, E>` discriminated union type for all async operations
  (ok/error pattern, not exceptions).
- Separate `RequestData` interfaces (snake_case fields for API) from display
  interfaces (camelCase fields).
- camelCase for variables/functions, PascalCase for components/interfaces/types.
- camelCase for `.ts` filenames, PascalCase for `.vue` filenames.

### Port/Adapter Pattern

Frontend mirrors the backend pattern: ports are TypeScript interfaces in
`src/ports/`, adapters in `src/adapters/`, selected via Pinia adapter store.

### Internationalization

All user-facing strings must use `t('key')` from `i18next-vue`.

## Test Patterns — Python

- **pytest** with `pytest-asyncio`, `pytest-mock`.
- Tests grouped in classes (e.g., `class TestAppEndpoints`).
- Factory fixtures returning async callables for test data setup.
- Use `mocker.AsyncMock()` for mocking async port methods.
- Use `TestClient` from Starlette for route tests.
- Test markers: `e2e`, `e2e_udm` (management-api); `integration`,
  `in_container_test` (authorization-api).
- Coverage omits `*/ports/*` — test adapters, not port interfaces.
