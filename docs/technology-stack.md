# Guardian -- Technology Stack Analysis

**Date:** 2026-03-29

## Overview

Guardian is a monorepo containing 5 distinct parts, spanning Python backend services, a shared Python library, a Python client SDK, and a Vue 3 frontend. All backend services share a common hexagonal (ports and adapters) architecture pattern. OPA (Open Policy Agent) serves as the external policy evaluation engine.

---

## Part 1: Management API (`management-api/`)

**Project Type:** Backend API Service
**Architecture Pattern:** Hexagonal (Ports & Adapters)

### Technology Table

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| Language | Python | ^3.11 | Primary backend language across all Guardian services |
| Framework | FastAPI | <0.200 | Async REST API framework with OpenAPI/Swagger support |
| ASGI Server | Uvicorn | ^0.38.0 | ASGI server for FastAPI (dev mode with `--reload`) |
| Process Manager | Gunicorn | ^23.0.0 | Production WSGI/ASGI process manager with Uvicorn workers |
| ORM | SQLAlchemy | ^2.0.44 | Async ORM for database persistence (all entity adapters) |
| Migrations | Alembic | ^1.17.2 | Database schema migration tool (3 migrations: 1.0.0, 2.0.0, 3.0.4) |
| Data Validation | Pydantic | ^2.12.5 | Request/response model validation and serialization |
| Settings | Pydantic-Settings | ^2.12.0 | Environment-variable-based configuration via adapter selection |
| JSON Serialization | orjson | ^3.11.4 | Fast JSON serialization (default FastAPI response class) |
| HTTP Client | httpx | ^0.28.1 | Async HTTP client (used by GuardianAuthorizationAdapter for M2M auth) |
| Logging | Loguru | ^0.7.3 | Structured logging with correlation ID support |
| Auth Library | Authlib | ^1.6.5 | OAuth2/OIDC token handling |
| Async SQLite | aiosqlite | ^0.21.0 | Async SQLite driver (development database backend) |
| Async PostgreSQL | asyncpg | ^0.31.0 | Async PostgreSQL driver (production database backend) |
| Async File I/O | aiofiles | ^25.1.0 | Async file operations (bundle server) |
| Async Shell Utils | aioshutil | ^1.6 | Async file copy/move (bundle generation) |
| Version Utils | packaging | ^24.1 | Version string parsing |
| Adapter Registry | guardian-lib | 1.8.1 | Internal shared library (port-loader, auth adapters, settings) |
| Package Manager | Poetry | -- | Dependency management and packaging |
| Containerization | Docker | -- | Multi-stage Dockerfile (builder, dev, production targets) |

### Dev/Test Dependencies

| Category | Technology | Version |
|----------|-----------|---------|
| Test Framework | pytest | ^9.0.1 |
| Async Tests | pytest-asyncio | ^1.3.0 |
| Mocking | pytest-mock | ^3.15.1 |
| Coverage | pytest-cov | ^7.0.0 |
| Test Env Vars | pytest-env | ^1.2.0 |
| Crypto (test JWT) | cryptography | ^46.0.3 |

---

## Part 2: Authorization API (`authorization-api/`)

**Project Type:** Backend API Service (v3.0.6)
**Architecture Pattern:** Hexagonal (Ports & Adapters)
**Source Lines:** ~2,506 (application) + ~801 (vendored UDM client) + ~2,893 (tests)

### Technology Table

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| Language | Python | ^3.11 | Shared language with management-api |
| Framework | FastAPI | ^0.135.1 | Async REST API for authorization decisions |
| ASGI Server | Uvicorn | ^0.38.0 | ASGI server |
| Process Manager | Gunicorn | ^23.0.0 | Production process manager |
| Data Validation | Pydantic | ^2.12.5 | Request/response validation (route model layer) |
| Settings | Pydantic-Settings | ^2.12.0 | Env-var configuration via `AdapterSelection` class |
| JSON Serialization | orjson | ^3.11.4 | Fast JSON (default FastAPI response class: `ORJSONResponse`) |
| OPA Client | opa-client | ^1.0.3 | Communicates with OPA for policy evaluation (private Univention registry) |
| HTTP Client | requests | ^2.32.5 | Sync HTTP client (vendored UDM REST API client, OAuth well-known) |
| URI Templates | uritemplate | ^4.2.0 | URI template expansion for vendored UDM client HAL+JSON navigation |
| Logging | Loguru | ^0.7.3 | Structured logging with per-request correlation IDs via `X-Request-ID` header |
| Version Utils | packaging | ^24.1 | Version parsing |
| Adapter Registry | guardian-lib | 1.8.1 | Shared library (port-loader, auth adapters, settings) |
| Package Manager | Poetry | -- | Dependency management |
| Containerization | Docker | -- | Multi-stage Dockerfile |

### Ports and Adapters

| Port | Adapter(s) | Entry Point Alias | Env Var |
|------|-----------|-------------------|---------|
| `SettingsPort` | `EnvSettingsAdapter` | `env` | `GUARDIAN__AUTHZ__ADAPTER__SETTINGS_PORT` |
| `PersistencePort` | `UDMPersistenceAdapter` | `udm_data` | `GUARDIAN__AUTHZ__ADAPTER__PERSISTENCE_PORT` |
| `PolicyPort` | `OPAAdapter` | `opa` | `GUARDIAN__AUTHZ__ADAPTER__POLICY_PORT` |
| `AuthenticationPort` | `FastAPIAlwaysAuthorizedAdapter`, `FastAPINeverAuthorizedAdapter`, `FastAPIOAuth2` | `fast_api_always_authorized`, `fast_api_never_authorized`, `fast_api_oauth2` | `GUARDIAN__AUTHZ__ADAPTER__AUTHENTICATION_PORT` |
| `GetPermissionsAPIPort` | `FastAPIGetPermissionsAPIAdapter` | (hardcoded) | -- |
| `CheckPermissionsAPIPort` | `FastAPICheckPermissionsAPIAdapter` | (hardcoded) | -- |

### Model Layers (4 layers)

| Layer | Location | Type | Purpose |
|-------|----------|------|---------|
| Route models | `models/routes.py` | Pydantic `BaseModel` | HTTP request/response serialization |
| Domain models | `models/policies.py` | Frozen `@dataclass` | Business logic and port interfaces |
| Persistence models | `models/persistence.py` | `@dataclass` | Data storage representation (UDM objects) |
| OPA models | `models/opa.py` | Frozen `@dataclass` | OPA wire format (camelCase field names) |

### API Endpoints (5 routes)

| HTTP Method | Path | Description |
|-------------|------|-------------|
| POST | `/permissions` | Get all permissions for actor + targets (direct) |
| POST | `/permissions/with-lookup` | Get permissions with actor/target UDM lookup |
| POST | `/permissions/check` | Check specific permissions (direct) |
| POST | `/permissions/check/with-lookup` | Check permissions with actor/target UDM lookup |
| POST | `/permissions/custom/{app}/{ns}/{endpoint}` | Custom policy endpoint (NOT IMPLEMENTED) |

### Notable Components

- **Vendored UDM client** (`udm_client.py`, 801 lines): Synchronous HTTP client for the UCS UDM REST API using HAL+JSON hypermedia format. Includes retry logic (5 retries with `Retry-After`), basic and bearer auth, and a full exception hierarchy. Vendored because no pip-installable client exists.
- **Correlation ID middleware**: Extracts `X-Request-ID` from request headers (or generates UUID4), sets it in a `ContextVar` for structured logging, and adds it to response headers.
- **Two-phase logger initialization**: Configures with defaults at startup, then reconfigures with settings from the `SettingsPort` after adapters are loaded.
- **General permissions pattern**: OPA queries for "general" (non-target-specific) permissions append an empty target sentinel; responses for the empty target ID are extracted as general permissions.

### Dev/Test Dependencies

| Category | Technology | Version |
|----------|-----------|---------|
| Test Framework | pytest | ^9.0.1 |
| Async Tests | pytest-asyncio | ^1.3.0 |
| Mocking | pytest-mock | ^3.15.1 |
| Coverage | pytest-cov | ^7.0.0 |
| Test Data | Faker | ^38.2.0 |
| HTTP Test Client | httpx | ^0.28.1 |
| Crypto (test JWT) | cryptography | ^46.0.3 |

### Test Coverage Summary

| Test Module | Tests | Focus |
|-------------|-------|-------|
| `test_main.py` | 4 | App setup, CORS middleware |
| `test_business_logic.py` | 2 | Call chain verification (get/check permissions) |
| `test_authentication.py` | 7 | OAuth2 token validation (valid, expired, wrong key, etc.) |
| `test_adapter_registry.py` | 2 | Env var reading, registry configuration sequence |
| `routes/test_get_permissions.py` | 5 unit + 7 integration | Get-permissions endpoint (lookup, errors, OPA errors) |
| `routes/test_permissions_check.py` | 6 unit + 7 integration | Check-permissions endpoint (lookup, errors) |
| `adapters/test_api.py` | 7 | API adapter model conversion |
| `adapters/test_persistence.py` | 9 unit + 4 integration | UDM adapter (errors, role parsing, caching) |
| `adapters/test_policies.py` | 6 unit + 3 integration | OPA adapter (errors, upstream errors, faulty data) |

---

## Part 3: Guardian Lib (`guardian-lib/`)

**Project Type:** Shared Python Library
**Architecture Pattern:** Hexagonal (Ports & Adapters) -- provides base port/adapter infrastructure

### Technology Table

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| Language | Python | ^3.11 | Shared across all Python parts |
| Adapter Framework | port-loader | 1.2.0 (pinned) | Core hexagonal architecture registry; loads adapters from entry points |
| Lazy Initialization | lazy-object-proxy | ^1.12.0 | Defers adapter registry instantiation until first use |
| Data Validation | Pydantic | ^2.12.5 | Transitive requirement for consuming services |
| Settings | Pydantic-Settings | ^2.12.0 | Transitive requirement |
| Web Framework | FastAPI | <0.200 | Authentication adapters depend on FastAPI Request type |
| JWT | PyJWT | ^2.10.1 | JWT token decoding and RS256 signature validation |
| HTTP Client | requests | ^2.32.5 | Fetches OAuth well-known configuration endpoints |
| Logging | Loguru | ^0.7.3 | Structured logging configuration shared across services |
| Package Manager | Poetry | -- | Dependency management |

### Dev/Test Dependencies

| Category | Technology | Version |
|----------|-----------|---------|
| Test Framework | pytest | ^9.0.1 |
| Async Tests | pytest-asyncio | ^1.3.0 |
| Mocking | pytest-mock | ^3.15.1 |
| Coverage | pytest-cov | ^7.0.0 |
| Crypto (test JWT) | cryptography | ^46.0.3 |

---

## Part 4: Authorization Client (`authorization-client/`)

**Project Type:** Python Client SDK / Library
**Architecture Pattern:** Imperative client with optional local policy evaluation

### Technology Table

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| Language | Python | ^3.11 | Shared language |
| HTTP Client | requests | ^2.28.0 | Sync HTTP client for Guardian API communication |
| YAML Parser | PyYAML | ^6.0 | Parses authorization configuration YAML files |
| LDAP | python-ldap | ^3.4 | DN parsing and comparison for LDAP scope checks (subtree, base, one) |
| Package Manager | Poetry | -- | Dependency management |

### Dev/Test Dependencies

| Category | Technology | Version |
|----------|-----------|---------|
| Test Framework | pytest | ^9.0.1 |
| Coverage | pytest-cov | ^7.0.0 |
| Mocking | pytest-mock | ^3.15.1 |

---

## Part 5: Management UI (`management-ui/`)

**Project Type:** Web Frontend (Single Page Application)
**Architecture Pattern:** Hexagonal (Ports & Adapters) with Pinia state management

### Technology Table

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| Language | TypeScript | ~5.9.3 | Type-safe frontend development |
| Framework | Vue 3 | ^3.5.25 | Reactive UI framework with Composition API (`<script setup>`) |
| State Management | Pinia | ^3.0.4 | Official Vue 3 state management; used for adapter wiring |
| Router | vue-router | ^4.6.3 | Client-side routing with web history mode |
| Build Tool | Vite | ^7.2.6 | Fast development server and production bundler |
| UI Component Library | @univention/univention-veb | 0.0.68 | Univention Vue Enterprise Base components (UGrid, UConfirmDialog, etc.) |
| Authentication | keycloak-js | 26.0.5 | Keycloak OIDC/SSO client with PKCE support |
| i18n | i18next | ^25.6.3 | Internationalization framework (English + German) |
| i18n Vue Binding | i18next-vue | ^5.3.1 | Vue 3 integration for i18next |
| UUID | uuid | ^13.0.0 | Unique identifier generation |
| CSS Preprocessor | Stylus | ^0.64.0 | CSS preprocessing in `<style lang="stylus">` blocks |
| Package Manager | Yarn | 1.22.22 | Frontend dependency management |
| Containerization | Docker + nginx | -- | Nginx-based production container with runtime config generation |

### Dev/Test Dependencies

| Category | Technology | Version |
|----------|-----------|---------|
| E2E Testing | Playwright | ^1.57.0 |
| Unit Testing | Vitest | ^4.0.14 |
| Vue Test Utils | @vue/test-utils | ^2.4.6 |
| DOM Environment | jsdom | ^27.2.0 |
| Linting | ESLint | ^10.0.2 |
| Vue Linting | eslint-plugin-vue | ^10.6.2 |
| Formatting | Prettier | ^3.7.3 |
| Type Checking | vue-tsc | ^3.1.5 |
| Vite Vue Plugin | @vitejs/plugin-vue | ^6.0.2 |
| URL Rewriting | vite-plugin-rewrite-all | ^1.0.2 |

---

## Infrastructure Components

### OPA (Open Policy Agent)

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| Policy Engine | OPA | 1.11.0 | External policy evaluation engine; evaluates Rego policies |
| Policy Language | Rego | v0-compatible | Declarative policy language for ABAC permission evaluation |
| Deployment | Docker | -- | Standalone container polling Management API for bundles |

### Keycloak (Identity Provider)

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| IdP | Keycloak | (from base image) | OAuth2/OIDC identity provider for all Guardian services |
| Provisioning | Python script | -- | `configure.py` provisions realm and client configurations |

### Development Orchestration

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| Orchestration | Docker Compose | -- | `dev-compose.yaml` orchestrates 8 services for local development |
| Reverse Proxy | Traefik | v2.11 | Routes all services under `/guardian/*` paths |
| Database (dev) | SQLite | -- | Default development database (via aiosqlite) |
| Database (prod) | PostgreSQL | -- | Production database (via asyncpg, enabled by `dev-compose-postgres.yaml`) |

### CI/CD

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| CI Platform | GitLab CI | -- | Pipeline defined in `.gitlab-ci.yml` |
| Container Builds | Kaniko | -- | Rootless Docker image building in CI |
| Linting | pre-commit | -- | Runs Black, Ruff, Bandit, mypy, pymarkdown (in isolated environments) |
| Code Quality | SonarQube | -- | Static analysis across all Python subprojects |
| Docs | Sphinx | -- | Builds Guardian Manual, Developer Reference, Architecture docs |
| Package Registry | GitLab PyPI | -- | Publishes guardian-lib and authorization-client packages |
| App Release | UCS App Center | -- | Three separate release pipelines for authz-api, management-api, management-ui |

### Cross-Cutting Tools

| Category | Technology | Purpose |
|----------|-----------|---------|
| Formatter (Python) | Black 24.10.0 | Code formatting (via pre-commit only) |
| Linter (Python) | Ruff | Import sorting, error/style checks (E, F, I rules) |
| Type Checker | mypy 1.13.0 | Static type checking with Pydantic plugin (via pre-commit only) |
| Security Scanner | Bandit 1.7.10 | Python security analysis (via pre-commit only) |
| SBOM | generate-filesystem-sbom | Software Bill of Materials generation for Docker images |
| Dependency Updates | Renovate | Automated dependency update PRs |

---

## Architecture Patterns Summary

| Part | Pattern | Key Characteristics |
|------|---------|-------------------|
| management-api | Hexagonal / Ports & Adapters | 10 ports, entry-point-based adapter loading, 3 model layers (domain/router/SQL), single `business_logic.py` |
| authorization-api | Hexagonal / Ports & Adapters | 4+2 ports, entry-point-based adapter loading, 4 model layers (domain/route/OPA/persistence) |
| guardian-lib | Hexagonal / Ports & Adapters | Base port/adapter infrastructure, `port-loader` registry, FastAPI dependency injection via `port_dep()` |
| authorization-client | Imperative Client | Remote HTTP + local file-based evaluation, LRU-cached token management, idempotent create-or-modify |
| management-ui | Hexagonal / Ports & Adapters | TypeScript port interfaces, Pinia store adapter wiring via switch/case on config strings |

---

_Generated using BMAD Method `document-project` workflow_
