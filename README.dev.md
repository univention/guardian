# Developing Guardian

- `./dev-run`: Run Guardian in development mode with hot-reloading.
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

First you need to follow the setup steps above.

### Management API Tests

The management-api tests can be run directly without special setup:

```bash
docker exec management-guardian-dev pytest -v /app/management-api/tests/
```

For more details, see the [management-api README](management-api/README.md).

### Authorization API Tests

The authorization-api has integration tests that require OPA to be loaded with test data.
By default, the dev environment loads production data from Alembic migrations, which will
cause the OPA integration tests to fail.

To run the integration tests:

1. Ensure the dev environment is running:

   ```bash
   ./dev-run
   ```

1. Load the test mapping data into OPA:

   ```bash
   # Copy test mapping to the bundle build directory
   docker cp management-api/rego_policy_bundle_template/univention/test_mapping/data.json \
      management-guardian-dev:/guardian_service_dir/bundle_server/build/GuardianDataBundle/guardian/mapping/data.json

   # Rebuild the OPA data bundle
   docker exec management-guardian-dev opa build --v0-compatible -b /guardian_service_dir/bundle_server/build/GuardianDataBundle \
      -o /guardian_service_dir/bundle_server/bundles/GuardianDataBundle.tar.gz

   ```

1. Wait for OPA to pick up the new bundle.

1. Run the tests inside the container:

   ```bash
   docker exec authz-guardian-dev pytest -v /app/authorization-api/tests/
   ```

**Note:** After restarting the dev environment or if the management-api regenerates bundles,
the test data will be overwritten with production data. You'll need to repeat step 2.

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
