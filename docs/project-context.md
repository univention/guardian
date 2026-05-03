---
project_name: 'guardian'
user_name: 'Nubus Core team'
date: '2026-03-28'
sections_completed:
  ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'quality_rules', 'workflow_rules', 'anti_patterns']
status: 'complete'
rule_count: 127
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

**Backend (Python):**

| Technology | Version | Notes |
|---|---|---|
| Python | ^3.11 | Target: `py311` |
| FastAPI | <0.200 (mgmt/lib), ^0.135.1 (authz) | With `ORJSONResponse` default. **Versions differ between services -- check each service's pyproject.toml before using any FastAPI feature.** |
| Pydantic | ^2.12.5 | `ConfigDict`, NOT v1 `class Config` |
| pydantic-settings | ^2.12.0 | Separate package for `BaseSettings` classes |
| SQLAlchemy | ^2.0.44 (async) | ORM models prefixed with `DB` |
| Alembic | ^1.17.2 | Database migrations |
| **port-loader** | **1.2.0 (exact pin)** | **Keystone dependency -- entire plugin system depends on it. Any version change could break adapter loading.** |
| Poetry | 1.8.4 | Dependency management + adapter entry points |
| loguru | ^0.7.3 | NOT stdlib `logging` |
| pytest | ^9.0.1 | All services |
| pytest-asyncio | ^1.3.0 | `asyncio_mode = "auto"` is NOT configured -- tests need explicit `@pytest.mark.asyncio` |
| Faker | ^38.2.0 | Test data generation (authorization-api only) |

**Frontend:**

| Technology | Version | Notes |
|---|---|---|
| TypeScript | ~5.9.3 | Strict mode, tilde-pinned (patch updates only) |
| Vue | ^3.5.25 | Composition API (`<script setup lang="ts">`) |
| Vite | ^7.2.6 | Build tool |
| Pinia | ^3.0.4 | State management (v3) |
| Playwright | ^1.57.0 | E2E testing |
| Vitest | ^4.0.14 | Unit testing (**v4 -- breaking changes from v3, use v4 APIs**) |
| @vue/test-utils | ^2.4.6 | Vue component unit testing |
| Yarn | 1.22.22 | Frontend package manager |
| ESLint | ^10.0.2 | Flat config format (v10) |
| Prettier | ^3.7.3 | Frontend formatting |

**Infrastructure / Tooling:**

| Technology | Version | Notes |
|---|---|---|
| OPA / Rego | pre-commit-opa v1.5.1, Regal v0.29.2 | Policy engine |
| Keycloak | keycloak-js 26.0.5 | OAuth2/OIDC identity provider |
| Black | 24.10.0 | Line length: 105 (**pre-commit only**) |
| Ruff | v0.8.0 | Rules: E, F, I (**pre-commit only**) |
| mypy | v1.13.0 | Pydantic plugin (**pre-commit only**) |
| Bandit | 1.7.10 | Security linter (**pre-commit only**) |

**Key version constraints:**
- Pydantic v2 is mandatory -- never use v1 patterns (`class Config` -> `model_config = ConfigDict(...)`)
- Python 3.11+ required (used in type hints, async features)
- Vue 3 Composition API only -- no Options API
- **Black, Ruff, mypy, Bandit are NOT dev dependencies** -- they exist only in pre-commit's isolated environments. Run them exclusively via `pre-commit run --all-files`, never `pip install` or run directly.
- **FastAPI version constraints differ between services**: management-api/guardian-lib use `<0.200` (broad), authorization-api uses `^0.135.1` (narrower). Always check the specific service's pyproject.toml.
- **`authorization-client`** (v0.1.0) is a separate, simpler sync-only component using `requests`, `pyyaml`, and `python-ldap` -- no async, no FastAPI. Patterns are completely different from the other services.
- **`pytest-env`** (^1.2.0) is only available in management-api (testing group) -- not present in other services.

## Critical Implementation Rules

### Language-Specific Rules

**Python:**
- **Use `loguru` for logging**, never `import logging`. Configure via `guardian_lib.logging.configure_logger`. Bind correlation IDs with `loguru.logger.bind()`.
- **Pydantic v2 only**: Use `model_config = ConfigDict(...)` instead of inner `class Config`. Use `model_dump()` not `.dict()`, `model_validate()` not `.parse_obj()`. **Note:** port-loader adapters use a separate `class Config` with `alias` -- this is port-loader's mechanism, NOT Pydantic's config. Do not "fix" adapter `class Config` blocks.
- **Domain models are `@dataclass`**, NOT Pydantic models. Frozen dataclasses for query objects (`@dataclass(frozen=True)`).
- **Async everywhere**: All persistence and business logic functions are `async`. Use `pytest.mark.asyncio` for async tests. **Exception:** `authorization-client` is synchronous -- uses `requests`, `python-ldap`, and standard sync patterns. Do not apply async patterns to it.
- **Type hints are mandatory**: mypy with pydantic plugin enforced. Use `Optional[T]` or `T | None` (Python 3.11+ syntax OK). Do NOT add `from __future__ import annotations` -- the project targets 3.11+ and uses native syntax directly.
- **Relative imports** within the same service package (e.g., `from ..models.role import Role`). Absolute imports for cross-package references (e.g., `from guardian_lib.ports import SettingsPort`).
- **Use f-strings** for string formatting. Not `%` formatting, not `.format()`.
- **Ellipsis (`...`) for empty bodies**, not `pass`. Used consistently for empty exception classes, abstract methods, and placeholder bodies:
  ```python
  class ObjectNotFoundError(ValueError):
      ...  # correct -- not `pass`
  ```
- **`python-ldap`** is a C extension isolated to `authorization-client`. Do not introduce it in other services.
- **AGPL-3.0-only license header** required on every file:
  ```python
  # Copyright (C) 2023 Univention GmbH
  #
  # SPDX-License-Identifier: AGPL-3.0-only
  ```

**TypeScript/Vue:**
- **Composition API only** with `<script setup lang="ts">` -- never Options API.
- **Stylus** for CSS preprocessing in Vue components.
- **`@` path alias** maps to `./src` in imports.
- **i18next** for all user-facing strings -- never hardcode display text.
- **`@univention/univention-veb`** component library for all UI components.
- **ESLint flat config format (v10)** -- uses `eslint.config.js`, NOT legacy `.eslintrc`. Use the new flat config API for any ESLint customization.
- **`@typescript-eslint/no-explicit-any` is intentionally OFF** -- do not add `any` type restrictions or "fix" `any` types unless specifically asked.
- **Unused variables must be prefixed with `_`** -- ESLint enforces `no-unused-vars: error` with `^_` ignore patterns for args, vars, and caughtErrors. Prefix unused variables with `_`, do not remove them.

### Framework-Specific Rules

**Capability vs Privilege Terminology:**
- The term **capability** is deprecated and will be replaced by **privilege** in a future refactoring. The rename has NOT yet been applied -- the entire codebase (filenames, class names, API endpoints, route names, DB models, frontend TypeScript, Rego policies) uniformly uses "capability." **Always use "capability" in code to match the existing codebase.** In new documentation, prefer "privilege." The two terms are synonymous.

**FastAPI / Hexagonal Architecture:**
- **Hexagonal Architecture (Ports & Adapters)** is the core pattern. Every service has: `ports/` (abstract interfaces), `adapters/` (concrete implementations), `models/` (data), `routers/` (thin HTTP layer).
- **All business logic lives in `business_logic.py`** -- routers and adapters NEVER contain business logic. Routers are thin wrappers that delegate to business logic functions.
- **Port-loader adapter registration** via Poetry entry points in `pyproject.toml`:
  ```toml
  [tool.poetry.plugins."<package_name>.<PortClassName>"]
  "<adapter_key>" = "<module_path>:<AdapterClass>"
  ```
- **Adapter selection via environment variables**: `GUARDIAN__<SERVICE>__ADAPTER__<PORT_NAME>` (double underscores). E.g., `GUARDIAN__MANAGEMENT__ADAPTER__SETTINGS_PORT=env`.
- **`AdapterSelection`** is a Pydantic `BaseSettings` class in `adapter_registry.py`. Each field has an `alias` matching the port class name exactly.
- **Dependency injection** via `Depends(port_dep(PortClass))` for persistence ports (adapter selected from config) and `Depends(port_dep(PortClass, AdapterClass))` for API ports (adapter specified explicitly).
- **Every adapter** that loads via entry points must have an inner `class Config` with `alias` matching its entry point key. Persistence adapters that need configuration extend `AsyncConfiguredAdapterMixin`. Persistence adapters also set `cached = True`.
- **Three-layer model discipline**:
  - Domain: `@dataclass` classes (plain Python)
  - Router: Pydantic `BaseModel` subclasses (API serialization)
  - Persistence: SQLAlchemy ORM models with `DB` prefix
  - Adapters translate between these layers -- they are NEVER the same classes.
- **Router conventions**: Every route handler receives `request: Request`, `authc_port`, and `authz_port` dependencies. POST uses `status_code=201`. **PATCH for most entity updates, but capability uses PUT (full replacement semantics).** Currently only capability has DELETE (`status_code=204`) -- other entities are missing DELETE endpoints (not yet implemented, not a deliberate omission).
- **Two router delegation styles exist**: (A) Call `.model_dump()` on response in router (app, role -- preferred for new code), (B) Return Pydantic model directly (capability). **Prefer Style A for consistency.**
- **Response wrapping**: Single entity: `{"role": {...}}`, multiple: `{"roles": [...], "pagination": {...}}`. The key is always the singular/plural of the entity name.
- **Error handling**: Domain errors (`ObjectNotFoundError`, `ObjectExistsError`, etc.) are translated to HTTP errors by `TransformExceptionMixin` in the API adapter layer. Never catch errors in routers. Each entity has its own `Transform<Entity>ExceptionMixin` subclass.
- **`error_guard` decorator** wraps all SQLAlchemy operations to convert `SQLAlchemyError` into `PersistenceError`.
- **Known inconsistency**: Namespace business logic functions accept `FastAPINamespaceAPIAdapter` (concrete type) instead of the abstract port. Do NOT replicate this pattern in new code -- always use abstract port types in business logic signatures.
- **`custom_endpoint.py`** is a stub router with hardcoded dummy data and no auth/port dependencies. **Never use it as a template for new routers.**

**Vue 3 Frontend:**
- **Mirrors the backend hexagonal architecture**: `ports/` (TypeScript interfaces), `adapters/` (implementations), `stores/` (Pinia state management).
- **Adapter selection** in frontend is done via settings store with a `switch/case` pattern, not entry points. **Always include a `default` case that throws `InvalidAdapterError`** when adding new adapter selection logic.
- **Pinia stores** use Composition API style (`defineStore` with setup function), not Options API style. The adapter store uses an unusual immediately-invoked factory pattern (`useAdapterStore(config)`) -- for new stores, follow the simpler `defineStore('name', () => { ... })` pattern used by settings and error stores.
- **Error handling** pushes to a global `useErrorStore` -- never throws directly from components.
- **Routes** follow REST-like camelCase naming: `listRoles`, `addRole`, `editRole`. Capabilities are nested under role edit routes. Generic `ListView`/`EditView` components are reused with `objectType` and `action` props.
- **Frontend test routes** are conditionally included via `VITE__MANAGEMENT_UI__TESTING__ENABLE_TEST_ROUTES` env var. New test views must follow this gating pattern.
- **Known typo**: The frontend route path for capabilities is misspelled as `capabilties` (missing 'i'). This is baked into production URLs -- do NOT "fix" it without a migration plan.
- **`KeepAlive`** wraps `ListView` for caching.
- **App init flow**: `i18n init -> createApp -> mount -> settingsStore.init() -> adapter init -> authenticate()`.

**OPA / Rego:**
- **Policy bundle template** lives in `management-api/rego_policy_bundle_template/`.
- **Builtin conditions** are stored as JSON + Rego files in `management-api/alembic/<version>_builtin_conditions/`.
- **Pre-commit hooks** validate Rego: `opa-fmt`, `opa-check`, `opa-test`, `regal-lint`.

### Testing Rules

**Backend (pytest):**
- **Tests run inside Docker containers**: `docker exec management-guardian-dev pytest -v /app/management-api/tests/` (management-api), `docker exec authz-guardian-dev pytest -v /app/authorization-api/tests/` (authorization-api).
- **Custom pytest markers** (differ by service):
  - `e2e` -- full integration tests against routes (management-api)
  - `e2e_udm` -- tests requiring a UDM instance (management-api)
  - `integration` -- integration tests (authorization-api)
  - `in_container_test` -- tests that must run in Docker (authorization-api)
- **`@pytest.mark.asyncio` is mandatory on every async test** -- `asyncio_mode = "auto"` is NOT configured in any service. Without this decorator, async tests silently pass without executing.
- **Session-scoped event loop**: Management-api overrides `event_loop` fixture to session scope (legacy pattern). The event loop is shared across the entire test session.
- **Registry setup in tests**: Create a fresh `AsyncAdapterRegistry`, manually register all port/adapter pairs, and set each adapter -- bypassing entry-point loading. Use `DummySettingsAdapter` for settings in tests.
- **Environment patching**: The `patch_env` fixture (session-scoped) sets all `GUARDIAN__*__ADAPTER__*` environment variables for adapter selection. Uses `os.environ` copy/clear/update (not `monkeypatch`) because it's session-scoped.
- **Database fixtures are function-scoped**: `create_tables` drops and recreates tables between tests. Use `@pytest.mark.usefixtures("create_tables")` per test method, not per class.
- **Custom `--real_db` pytest option** in management-api switches between SQLite (default) and real PostgreSQL. Tests must work in both modes.
- **Factory fixture pattern**: Entity creation fixtures return async factory functions:
  ```python
  @pytest.fixture
  def create_role():
      async def _create_role(session, app_name="app", ...):
          ...
      return _create_role
  ```
- **Route tests** are **synchronous** by default (Starlette `TestClient` in sync mode), marked with `@pytest.mark.e2e`. Use `app.url_path_for("create_app")` for URL resolution, not hardcoded paths. Some route tests are async when they need direct DB access after an HTTP call.
- **Adapter tests** are **pure unit tests** -- no database, no HTTP. They test `transform_exception`, `to_*` conversions, and model translation. Get the adapter via `registry_test_adapters.request_port(PortClass)`.
- **Authorization-api uses direct attribute monkey-patching** for mocking OPA and UDM clients (save original, replace, restore) instead of `mocker.patch()`.
- **Coverage configuration**: Management-api has BOTH `pyproject.toml` (omits `*/ports/*`) and `.coveragerc` (omits specific routers and ports). `.coveragerc` takes priority. No `fail_under` threshold is configured locally in any service -- CI jobs may add it as a CLI argument.

**Frontend:**
- **Vitest** (v4) for unit tests in `management-ui/src/tests/`. Environment: `jsdom`. Config explicitly excludes `e2e/*`.
- **Playwright** for E2E in `management-ui/e2e/`.
- **E2E locale**: `de-DE` with German language cookie `UMCLang=de` via storage state. All E2E assertions on user-facing text must use German translations.
- **CI E2E**: Headless chromium, 1 worker, 2 retries, base URL `http://localhost:5173`.

**OPA/Rego:**
- **Rego tests** validated via pre-commit hooks: `opa-test` runs policy tests automatically.

### Code Quality & Style Rules

**Linting & Formatting:**
- **Black** (24.10.0): Line length 105, target `py311`. Excludes `udm_client.py`. No config file -- runs via pre-commit only.
- **Ruff** (0.8.0): Rules `E` (pycodestyle errors), `F` (pyflakes), `I` (isort). Runs with `--fix` in pre-commit. Line length 105. **Canonical config is root `.ruff.toml`** -- modify that, not individual pyproject.toml files.
- **mypy**: Pydantic plugin enabled, `ignore_missing_imports = true`, **`disable_error_code = type-abstract`** (global -- do NOT add `# type: ignore[type-abstract]` comments; this is suppressed because port-loader instantiates abstract ports). Excludes `docs/` and `tests/`.
- **Bandit**: Security linter. Excludes all test directories and `udm_client.py`.
- **`udm_client.py`** is a legacy file excluded from Black, Ruff, Bandit, and mypy.
- **Frontend Prettier** (non-default settings): `singleQuote: true`, `bracketSpacing: false`, `printWidth: 120`, `trailingComma: "es5"`, `arrowParens: "avoid"`, `htmlWhitespaceSensitivity: "ignore"`, `semi: true`, `tabWidth: 2`.
- **Frontend ESLint**: Runs with `--max-warnings 0` -- any warning is a failure. Zero tolerance.
- **Frontend type checking**: `vue-tsc --noEmit` (stricter than plain `tsc`, includes Vue SFC type checking).
- **`pretty-format-json --autofix`** in pre-commit automatically reformats JSON files. Expect JSON changes to be auto-modified by the hook.

**Naming Conventions:**

| Item | Convention | Example |
|---|---|---|
| Python packages | `snake_case` | `guardian_management_api` |
| Port classes | `PascalCase` + `Port` suffix | `RolePersistencePort`, `RoleAPIPort` |
| Adapter classes | Technology prefix + `PascalCase` | `SQLRolePersistenceAdapter`, `FastAPIRoleAPIAdapter` |
| DB models | `DB` prefix + `PascalCase` | `DBRole`, `DBNamespace` |
| Domain models | Plain `PascalCase` dataclass | `Role`, `RoleGetQuery` |
| Router models | `PascalCase` with action suffix | `RoleCreateRequest`, `RoleSingleResponse` |
| Query dataclasses | `<Entity>GetQuery` / `<Entities>GetQuery` | `RoleGetQuery`, `RolesGetQuery` |
| Business logic functions | `snake_case` verbs | `create_role`, `get_roles` |
| Environment variables | `GUARDIAN__<SERVICE>__<SECTION>__<KEY>` | `GUARDIAN__MANAGEMENT__ADAPTER__SETTINGS_PORT` |
| Vue components | `PascalCase.vue` | `ListView.vue`, `EditView.vue` |
| Pinia stores | `use<Name>Store` | `useErrorStore`, `useAdapterStore` |
| Frontend ports/adapters | `<Technology><Port>Adapter` | `KeycloakAuthenticationAdapter` |

**Code Organization:**
- **Management object name validation**: Regex `^[a-z][a-z0-9\-_]*$` -- lowercase, starts with letter, only `[a-z0-9\-_]`.
- **String max length**: 256 characters for management object names.
- **Router models use heavy mixin composition**: `NameObjectMixin`, `AppNamePathMixin`, `NamespacePathMixin`, `PaginationRequestMixin`, `ResourceURLObjectMixin`, etc.
- **`GuardianBaseModel`** is the base for all router Pydantic models -- `model_config = ConfigDict(populate_by_name=True)`.

### Development Workflow Rules

**Development Environment:**
- **Docker Compose** is the primary dev environment: `dev-compose.yaml` (SQLite) or `dev-compose-postgres.yaml` (PostgreSQL). Reference the correct compose file for the context.
- **`dev-run`** script starts the full stack: Traefik (reverse proxy), OPA, Authorization API, Management API, Keycloak, Management UI.
- **CORS**: Configured via `GUARDIAN__MANAGEMENT__CORS__ALLOWED_ORIGINS` environment variable (comma-separated).
- **API prefix**: Management API routes are prefixed with `/guardian/management`. Frontend base path is `/univention/guardian/management-ui/`.
- **Frontend dev proxy**: When `VITE__MANAGEMENT_UI__CORS__USE_PROXY=1`, Vite proxies API requests to avoid CORS issues locally.

**Pre-commit Hooks (primary local quality gate):**
- **MANDATORY: Run `pre-commit run --all-files` after ANY code change.** This is required before commits, not optional.
- Hooks are **prefixed by category** for selective CI execution: `general-*`, `backend-*`, `frontend-*`.
- **General**: check-added-large-files, check-json/xml/yaml/toml, trailing-whitespace, pretty-format-json (autofix), **pymarkdown** (markdown formatting).
- **Backend**: black, bandit, mypy, ruff (with --fix), poetry-check (x4 packages), poetry-lock --check (x4), opa-fmt, opa-check, opa-test, regal-lint.
- **Frontend**: vue-tsc (type-check), yarn lint (`--max-warnings 0`), yarn format. All run from the `management-ui` directory.
- All hooks must pass before commits are accepted. Pre-commit is the primary local quality gate.
- **`poetry-lock --check` runs for all 4 packages.** If you modify one `pyproject.toml`, update its `poetry.lock` -- pre-commit will catch stale lock files. Ensure local Poetry version matches 1.8.4 (pre-commit hook version) to avoid lock file format changes.

**CI/CD (GitLab CI -- NOT GitHub Actions):**
- **Stages**: test -> build_python -> build_docker -> package -> publish -> build -> merge -> release -> production -> cleanup.
- **Pre-commit in CI** uses a `pre_commit_hook_parser.py` script to selectively run hooks by prefix category.
- **Coverage**: Each Python component has its own coverage job. `--fail-under` thresholds may be set in CI job configs (not in local coverage config files).
- **Docker builds**: Uses Kaniko. Separate images for: `guardian-opa`, `guardian-management-ui`, `guardian-authorization-api`, `guardian-management-api`.

**Multi-Package Repository:**
- This is a **monorepo** with 4 Python packages (`management-api`, `authorization-api`, `guardian-lib`, `authorization-client`) and 1 frontend app (`management-ui`).
- Each Python package has its own `pyproject.toml`, `poetry.lock`, and test suite.
- **Poetry** manages each package independently -- changes to one package may require updating others.
- **UCS App Center packaging** directories (`appcenter-authz/`, `appcenter-common/`, `appcenter-management/`, `appcenter-management-ui/`) contain Jinja-templated compose files and install scripts for deployment.

### Critical Don't-Miss Rules

**Anti-Patterns to Avoid:**
- **NEVER put business logic in routers or adapters.** All logic goes in `business_logic.py`. Routers only wire dependencies and delegate. Adapters only translate between layers.
- **NEVER use the same model class across layers.** Domain dataclasses, Pydantic router models, and SQLAlchemy DB models are always separate. Adapters translate between them.
- **NEVER use Pydantic v1 patterns.** No `.dict()`, `.parse_obj()`, `class Config`. Use `.model_dump()`, `.model_validate()`, `model_config = ConfigDict(...)`.
- **NEVER use stdlib `logging`.** Always `loguru`.
- **NEVER use PUT for updates** -- always PATCH. **Exception: capability uses PUT** (full replacement semantics).
- **NEVER catch domain errors in routers.** Errors flow through `TransformExceptionMixin` in the API adapter.
- **NEVER test port abstract classes directly.** Ports are excluded from coverage. Test the adapters.
- **NEVER use `asyncio.create_subprocess_shell` with f-string commands.** The existing `bundle_server.py` does this (known tech debt). New code must use `create_subprocess_exec` with explicit arguments to prevent shell injection.
- **NEVER use synchronous `requests` in async functions.** The existing `guardian_lib/adapters/authentication.py` uses `requests.get` inside `async def` (known tech debt -- blocks the event loop). New code must use `httpx.AsyncClient` for HTTP calls in async contexts.
- **NEVER use `assert` for validation in production code.** Assert statements are stripped with `-O` flag. Use explicit `if`/`raise` instead. (`authorization-client/authorization.py:171` has a known `assert` with `# nosec B101`.)

**Error Handling -- `transform_exception` Mapping:**

Management-API exception-to-HTTP mapping (`fastapi_utils.py`):

| Exception | HTTP Status | Notes |
|---|---|---|
| `ObjectNotFoundError` | 404 | With detail message |
| `ObjectExistsError` | 400 | With detail message |
| `UnauthorizedError` | 403 | Fixed message: "Not allowed." |
| `ValidationError` (Pydantic) | 422 | With detail message |
| `ParentNotFoundError` | 404 | With detail message |
| **Everything else** | **500** | **"Internal Server Error" -- no detail** |

**Unmapped exceptions that fall through to generic 500:** `PersistenceError`, `BundleGenerationIOError`, `BundleBuildError`, `AuthorizationError`. When adding new exception types, you must add a mapping or accept a generic 500.

**Inconsistency:** Authorization-API's `transform_exception` exposes `str(exc)` in 500 responses for `PersistenceError` and `PolicyUpstreamError`, while management-API returns only "Internal Server Error". The authz-API leaks internal error details to clients.

**Edge Cases Agents Must Handle:**
- **Adapter `class Config` with `alias`** is required on every adapter loadable via entry points -- forgetting it breaks the plugin system silently.
- **Adapter cache flag naming is inconsistent:** management-API uses `cached = True`, authorization-API and guardian-lib use `is_cached = True`. Match the convention of whichever service you're working in.
- **`AsyncAdapterSettingsProvider`** must be registered alongside `SettingsPort` -- this is easy to miss.
- **`error_guard` decorator** must wrap all SQLAlchemy operations -- raw SQLAlchemy exceptions must never escape adapters.
- **Correlation ID middleware** (`correlation_id.py`) must be preserved -- it provides request tracing via `X-Request-ID` header and loguru context binding. Note: no input validation on the header -- arbitrary strings are accepted (known tech debt).
- **`pragma: no cover`** should be used on abstract method `raise NotImplementedError` lines in ports.
- **Alembic migration gotchas:**
  - Migration 2.0.0 uses raw SQL (`op.execute()`) instead of Alembic ops -- dialect-dependent.
  - Builtin condition migrations depend on sibling filesystem paths (`../1.0.0_builtin_conditions/`). If directories are missing, migration silently inserts zero conditions.
  - `alembic/env.py` calls `asyncio.run()` -- crashes if called from within an existing event loop. Tests use `subprocess.check_call` to invoke Alembic in a separate process to avoid this.
- **Frontend string-matching error detection** (`data.ts:177`): Detects duplicate-name errors by exact string match against backend message. Known tech debt with `FIXME` comment. Do not replicate this pattern -- the backend should provide typed error codes.
- **Frontend `tryToJson<T>()`** casts `response.json()` to type `T` without runtime validation. Has a `TODO` comment acknowledging the gap.
- **Frontend init errors logged as `console.log`**, not `console.error` (`App.vue:33`). May be missed in production monitoring.
- **CORS header discrepancy**: management-API allows `X-Request-ID` in CORS headers, authorization-API does not. Cross-origin requests to the authz-API with `X-Request-ID` will fail CORS preflight.

**Security Rules:**
- **ABAC is enforced**: Every route handler must include both `authc_port` (authentication) and `authz_port` (authorization) dependencies. Never skip authorization checks.
- **`.env.example` ships with dangerous defaults** -- `RESOURCE_AUTHORIZATION_PORT=always` (authorization disabled) and `CORS=*` (any origin). Never copy `.env.example` as-is for deployment. Always set proper authorization adapter and CORS origins.
- **AGPL-3.0-only license**: Every source file must include the REUSE-compliant license header.
- **Bandit** scans all non-test Python code for security issues.
- **Environment variables** for secrets -- never hardcode credentials. Reference `.env.example` for the template.
- **JWT tokens are logged in warning messages** when invalid (`authentication.py:114`). This is a credential exposure risk. When modifying auth logging, sanitize tokens before logging.

**Performance Considerations:**
- **`ORJSONResponse`** is the default FastAPI response class -- do not switch to standard `JSONResponse`.
- **Adapter caching**: Persistence adapters with `Config.cached = True` (or `is_cached = True` in authz-API/guardian-lib) are singletons -- be aware of shared state.
- **`KeepAlive`** on `ListView` in the frontend -- component state persists across navigation.

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- **When you identify a new convention, lesson, or commit to a practice ("I'll make sure to..."), you MUST add it to this file immediately in the same session** -- verbal commitments are not persistent across story boundaries
- Update this file if new patterns emerge

**For Humans:**
- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Review quarterly for outdated rules
- Remove rules that become obvious over time

Last Updated: 2026-03-28
