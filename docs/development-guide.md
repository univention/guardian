# Development Guide -- Guardian

**Date:** 2026-03-29

---

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | ^3.11 | Backend services and libraries |
| Poetry | 2.2.1 | Python dependency management |
| Node.js | v24+ | Management UI build (Vite, Vitest, Playwright) |
| Yarn | 1.22.22 | Frontend dependency management |
| Docker + Docker Compose | latest | Local development environment |
| pre-commit | latest | Linting and formatting hooks |

---

## Quick Start (Docker)

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env as needed (UCS_HOST_IP, LDAP_BASE, etc.)

# 2. Start all services
docker compose -f dev-compose.yaml up --build

# 3. Access
# Management API docs:  http://localhost/guardian/management/docs
# Authorization API docs: http://localhost/guardian/authorization/docs
# Management UI:         http://localhost/univention/guardian/management-ui
# Keycloak admin:        http://localhost:8888  (Traefik dashboard)
```

The development stack runs 8 services via Docker Compose:

- **proxy** (Traefik v2.11) -- reverse proxy on port 80
- **management-api** -- FastAPI with hot-reload
- **authorization-api** -- FastAPI with hot-reload
- **management-ui** -- Vite dev server
- **opa** -- OPA v1.11.0, polls management-api for bundles
- **keycloak** -- Identity provider
- **keycloak-provisioning** -- One-shot realm/client setup
- **db** / **db_provisioning** -- SQLite (default) or PostgreSQL + Alembic migrations

### PostgreSQL Mode

```bash
docker compose -f dev-compose.yaml -f dev-compose-postgres.yaml up --build
```

---

## Local Development (Without Docker)

### Backend (management-api or authorization-api)

```bash
cd management-api  # or authorization-api
poetry install
poetry run uvicorn guardian_management_api.main:app --reload --host 0.0.0.0 --port 8000
```

### Shared Library (guardian-lib)

```bash
cd guardian-lib
poetry install
```

### Frontend (management-ui)

```bash
cd management-ui
yarn install
yarn dev          # Vite dev server with hot-reload
```

---

## Running Tests

### Management API

```bash
# All tests
poetry run pytest tests/

# Single file
poetry run pytest tests/test_business_logic.py

# Single test
poetry run pytest tests/routes/test_app.py::TestAppEndpoints::test_post_app_minimal

# By name pattern
poetry run pytest -k "test_post_app"

# Skip e2e tests
poetry run pytest -m "not e2e"

# Inside Docker dev container
docker exec management-guardian-dev pytest -v /app/management-api/tests/
```

### Authorization API

```bash
poetry run pytest tests/

# Integration tests require OPA with test data loaded
docker exec authz-guardian-dev pytest -v /app/authorization-api/tests/
```

### Guardian Lib

```bash
cd guardian-lib
poetry run pytest tests/
```

### Management UI

```bash
cd management-ui
yarn test:unit                           # Vitest (watch mode)
yarn test:unit --run                     # Single run
CI=1 yarn test:e2e --project=chromium    # Playwright E2E (headless)
CI=1 yarn test:e2e                       # All browsers
```

### OPA Policy Tests

```bash
opa test -b management-api/rego_policy_bundle_template -v
opa fmt -w management-api/rego_policy_bundle_template    # Format Rego
```

---

## Linting & Formatting

**Critical:** Black, Ruff, mypy, and Bandit are NOT dev dependencies. They exist only in pre-commit's isolated environments. Never install or run them directly.

```bash
# Run all linters (ALWAYS do this after changing any file)
pre-commit run --all-files

# Install hooks for automatic pre-commit checking
pre-commit install
```

### Tools (via pre-commit only)

| Tool | Version | Purpose | Config File |
|------|---------|---------|-------------|
| Black | 24.10.0 | Code formatting | `.black` |
| Ruff | latest | Import sorting + linting (E, F, I rules) | `.ruff.toml` |
| mypy | 1.13.0 | Static type checking (with Pydantic plugin) | `.mypy.ini` |
| Bandit | 1.7.10 | Security analysis | `.bandit` |

---

## Environment Variables

### Management API

| Variable | Default | Description |
|----------|---------|-------------|
| `GUARDIAN__MANAGEMENT__API_PREFIX` | `/guardian/management` | API URL prefix |
| `GUARDIAN__MANAGEMENT__CORS__ALLOWED_ORIGINS` | (none) | Comma-separated CORS origins |
| `GUARDIAN__MANAGEMENT__ADAPTER__SETTINGS_PORT` | -- | Settings adapter (`env`) |
| `GUARDIAN__MANAGEMENT__ADAPTER__APP_PERSISTENCE_PORT` | -- | App persistence (`sql`) |
| `GUARDIAN__MANAGEMENT__ADAPTER__NAMESPACE_PERSISTENCE_PORT` | -- | Namespace persistence (`sql`) |
| `GUARDIAN__MANAGEMENT__ADAPTER__ROLE_PERSISTENCE_PORT` | -- | Role persistence (`sql`) |
| `GUARDIAN__MANAGEMENT__ADAPTER__PERMISSION_PERSISTENCE_PORT` | -- | Permission persistence (`sql`) |
| `GUARDIAN__MANAGEMENT__ADAPTER__CONDITION_PERSISTENCE_PORT` | -- | Condition persistence (`sql`) |
| `GUARDIAN__MANAGEMENT__ADAPTER__CONTEXT_PERSISTENCE_PORT` | -- | Context persistence (`sql`) |
| `GUARDIAN__MANAGEMENT__ADAPTER__CAPABILITY_PERSISTENCE_PORT` | -- | Capability persistence (`sql`) |
| `GUARDIAN__MANAGEMENT__ADAPTER__AUTHENTICATION_PORT` | -- | Auth adapter (`fast_api_oauth`) |
| `GUARDIAN__MANAGEMENT__ADAPTER__RESOURCE_AUTHORIZATION_PORT` | -- | Authz adapter (`always`/`guardian`) |
| `SQL_PERSISTENCE_ADAPTER__DIALECT` | -- | `sqlite` or `postgresql` |
| `SQL_PERSISTENCE_ADAPTER__DB_NAME` | -- | Database name/path |
| `OAUTH_ADAPTER__WELL_KNOWN_URL` | -- | OIDC discovery URL |

### Authorization API

| Variable | Default | Description |
|----------|---------|-------------|
| `GUARDIAN__AUTHZ__API_PREFIX` | `/guardian/authorization` | API URL prefix |
| `GUARDIAN__AUTHZ__ADAPTER__SETTINGS_PORT` | -- | `env` |
| `GUARDIAN__AUTHZ__ADAPTER__PERSISTENCE_PORT` | -- | `udm_data` |
| `GUARDIAN__AUTHZ__ADAPTER__POLICY_PORT` | -- | `opa` |
| `GUARDIAN__AUTHZ__ADAPTER__AUTHENTICATION_PORT` | -- | Auth adapter |
| `OPA_ADAPTER__URL` | -- | OPA base URL |
| `UDM_DATA_ADAPTER__URL` | -- | UDM REST API URL |
| `UDM_DATA_ADAPTER__USERNAME` | -- | UDM username |
| `UDM_DATA_ADAPTER__PASSWORD` | -- | UDM password |

### Management UI (Vite)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE__MANAGEMENT_UI__ADAPTER__SETTINGS_PORT` | -- | `env` or `url` |
| `VITE__MANAGEMENT_UI__ADAPTER__AUTHENTICATION_PORT` | -- | `in_memory` or `keycloak` |
| `VITE__MANAGEMENT_UI__ADAPTER__DATA_PORT` | -- | `in_memory`, `test`, or `api` |
| `VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__SSO_URI` | -- | Keycloak URL |
| `VITE__KEYCLOAK_AUTHENTICATION_ADAPTER__REALM` | -- | Keycloak realm |
| `VITE__API_DATA_ADAPTER__URI` | -- | Management API URL |

---

## CI/CD Pipeline

**Platform:** GitLab CI (`.gitlab-ci.yml` + `.gitlab-ci/gitlab-ci.yml`)
**Stages:** test -> build_python -> build_docker -> package -> publish -> build -> merge -> release -> production -> cleanup

| Job Category | Jobs | Description |
|-------------|------|-------------|
| Pre-commit | 3 parallel | general, backend, frontend hook groups |
| Tests | 3 parallel | management-api, authorization-api, guardian-lib (pytest) |
| Python builds | 2 | guardian-lib, authorization-client (poetry build) |
| Docker builds | 4 | OPA, management-api, authorization-api, management-ui (Kaniko) |
| Publish | 2 (manual) | guardian-lib, authorization-client (GitLab PyPI) |
| Docs | 5 | Sphinx linkcheck, spelling, HTML, PDF, merge |
| Code quality | 1 | SonarQube analysis |
| App release | 3 | UCS App Center releases (one per deployable service) |

---

## Deployment

### Docker Images

| Image | Base | Build Context |
|-------|------|--------------|
| `guardian-management-api` | UCS base | `management-api/` |
| `guardian-authorization-api` | UCS base | `authorization-api/` |
| `guardian-management-ui` | nginx | `management-ui/` |
| `guardian-opa` | UCS base + OPA v1.11.0 | `opa/` |

### UCS App Center

Guardian is distributed as three separate Univention App Center applications:
- `guardian-authorization-api` (tag prefix: `authorization-api_`)
- `guardian-management-api` (tag prefix: `management-api_`)
- `guardian-management-ui` (tag prefix: `management-ui_`)

Each has its own release pipeline, Keycloak configuration, and App Center packaging in `appcenter-*/`.

---

_Generated using BMAD Method `document-project` workflow, Step 6_
