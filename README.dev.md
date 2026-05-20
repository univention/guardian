# Developing Guardian

A thorough project documentation including developer guidance can be found at [docs/index.md](docs/index.md).

A "cheat sheet" for roles, privilege/capabilities, and permissions is in [Guardian 3.0 Cheat Sheet](docs/guardian_cheat_sheet.pdf).

## Running Tests and Linters Without Local Setup

If you only need to run tests or linting, Docker is the only prerequisite.
This mirrors what CI runs and is useful for debugging CI failures locally.

```bash
# Run linters (pre-commit hooks)
docker compose run pre-commit

# Run tests
docker compose run --rm test
```

The pre-commit container uses a named volume to cache hook environments, so
repeat runs are significantly faster after the first one.

## Running Guardian

- `./dev-run`: Run Guardian in development mode.
- `./.env.example`: Example environment variables for development.

## Setup

1. Copy `./.env.example` to `./.env` and adjust any necessary environment variables.

   ```bash
   cp .env.example .env
   ```

1. Get a UCS VM and set its IP in `UCS_HOST_IP` in the `.env` file.
   It is used for the tests.

1. Create the filesystem SBOM for the Web UI so that the image builds locally.

   ```bash
   touch sbom-fs-management-ui.cdx.json
   ```

1. Use `./dev-run` to start Guardian in development mode.

   ```bash
   ./dev-run
   ```

1. Add `127.0.0.1 traefik` to your `/etc/hosts`, needed for the keycloak redirect to work

## Access to UI/API

- management-ui: http://localhost/univention/guardian/management-ui
  creds: `dev:univention` (see keycloak/provisioning/configure.py)
- keycloak admin console: http://traefik/guardian/keycloak/admin
  creds: `admin:admin` (see dev-compose.yaml)
- management API docs: http://localhost/guardian/management/docs
- authoriation API docs: http://localhost/guardian/authorization/docs
- OPA: http://localhost/guardian/opa/

## Troubleshooting

1. If you are having issues with Alembic, remove the folder `./management_service_dir`.
   Then recreate it with 1000 as owner before running `./dev-run` again.

1. If you get I/O permission errors, ensure that `./management_service_dir` is owned by user id 1000.

1. If you want to debug OPA, add the following to `opa/opa_config.yaml`:

   ```yaml
   decision_logs:
     console: true
   ```

## Running Tests

### Test categories

| Mark | Package | Requires | Default run |
|------|---------|---------|------------|
| _(none)_ | all | nothing | ✓ included |
| `e2e` | management-api | SQLite in-process, no external services | ✓ included |
| `e2e_udm` | management-api | Authorization API + Keycloak | excluded |
| `in_container_test` | authorization-api | OPA (skipped gracefully if absent) | ✓ included |
| `integration` | authorization-api | UDM | excluded |

### Management API Tests

Run standalone (e2e_udm excluded by default via pyproject.toml):

```bash
uv run pytest management-api/tests/
```

`e2e_udm` tests require the full dev stack (see Setup above). With the stack running,
pass `-m e2e_udm` to override the default exclusion:

```bash
docker exec management-guardian-dev pytest -v -m e2e_udm /app/management-api/tests/
```

For more details, see the [management-api README](management-api/README.md).

### Authorization API Tests

Run standalone (`integration` excluded by default; `in_container_test` runs but self-skips if OPA is absent):

```bash
uv run pytest authorization-api/tests/
```

`integration` tests require UDM credentials. Override `addopts` by passing `-m` explicitly:

```bash
uv run pytest -m integration authorization-api/tests/
```

For `in_container_test` (OPA) tests, use `docker compose run --rm test` as described at the top.

For more details, see the [authorization-api README](authorization-api/README.md).

### Management UI E2E Tests

The Management UI has end-to-end tests using Playwright. To run them:

1. Navigate to the management-ui directory:

   ```bash
   cd management-ui
   ```

1. Install dependencies if you haven't already:

   ```bash
   yarn install
   ```

1. Run the e2e tests:

   ```bash
   CI=1 yarn test:e2e --project=chromium
   ```

   **Note:** The `CI=1` environment variable enables headless mode, which is required for stable test execution.

1. To run tests for all browsers (chromium, firefox, webkit):

   ```bash
   CI=1 yarn test:e2e
   ```

1. To update screenshot snapshots after intentional UI changes:

   ```bash
   CI=1 yarn playwright test --project=chromium --update-snapshots
   ```

The tests use the "test" data adapter which provides mock data. The configuration is automatically loaded from `.env.development` when running the dev server.

For more details about the Management UI, see the [management-ui README](management-ui/README.md).
