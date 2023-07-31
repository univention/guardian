<!--
Copyright (C) 2023 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

# Guardian Management API

## Configuration

The app can be configured through the chosen adapter for the SettingsPort.

### Adapter settings

These settings are the only settings, that are always configured by providing environment variables instead of utilizing the SettingsPort.
These settings are also all required, and do not have any default value!

**GUARDIAN__MANAGEMENT__ADAPTER__SETTINGS_PORT,type=string**: Defines which adapter should be used for the settings port.
The project itself provides the `env` adapter, which can be used.

**GUARDIAN__MANAGEMENT__ADAPTER__APP_PERSISTENCE_PORT,type=string** Defines which adapter should be used for the app persistence port.
The project itself provides the `in_memory` adapter, which can be used.

### Logging

**guardian.management.logging.structured,type=bool,default=False**: If set to True, the logging output is structured as a JSON object

**guardian.management.logging.level,type=Enum,default=SUCCESS**: Sets the log level of the application. The choices are DEBUG, INFO,
WARNING, ERROR, CRITICAL.

**guardian.management.logging.format,type=string**: Defines the format of the log output, if not structured. The possible options are
described [here](https://loguru.readthedocs.io/en/stable/api/logger.html). The default is
`<green>{time:YYYY-MM-DD HH:mm:ss.SSS ZZ}</green> | <level>{level}</level> | <level>{message}</level> | {extra}`

**guardian.management.logging.backtrace,type=bool,default=False**: Whether the exception trace formatted should be
extended upward, beyond the catching point, to show the full stacktrace which generated the error.

**guardian.management.logging.diagnose,type=bool,default=False**: Whether the exception trace should display the variables
values to eases the debugging. This should be set to False in production to avoid leaking sensitive data.

## Adapters

The Guardian Management API provides some adapters, which are documented here

### EnvSettingsAdapter

**name**: env
**implements**: SettingsPort

The `EnvSettingsAdapter` loads settings exclusively from the environment. To find the correct environment variable
the setting name, e.g. *some.nested.important-option* is converted to uppercase and all dots are replace with double
underscores: *SOME__NESTED__IMPORTANT-OPTION*

### AppStaticDataAdapter

**name**: in_memory
**implements**: AppPersistencePort

The `AppStaticDataAdapter` stores data in memeory. This adapter is very rudimentary and not suitable for
production!

It does not require any settings.

### FastAPIAppAPIAdapter

**name**: fastapi
**implements**: AppAPIPort

The `FastAPIAppAPIAdapter` provides an adapter for the FastAPI framework. It is
used to expose the Guardian Management API.

It's used by default and partly configured by environment variables.

## Local development

### Running the Guardian Management API locally

To start the API on your local machine, follow these steps:

Prerequisites:

- Docker installed

```shell
# pwd == $REPO_DIR/management-engine/guardian/
cat > .env << EOF
GUARDIAN__MANAGEMENT__LOGGING__LEVEL=DEBUG
GUARDIAN__MANAGEMENT__LOGGING__STRUCTURED=0
GUARDIAN__MANAGEMENT__ADAPTER__SETTINGS_PORT=env
GUARDIAN__MANAGEMENT__ADAPTER__APP_PERSISTENCE_PORT=in_memory
EOF
cat > docker-compose.yaml << EOF
services:
  management-api:
    image: guardian-management:dev
    build:
      context: management-api/
      extra_hosts:
        - git.knut.univention.de:\${GITLAB_IP}
    ports:
      - 8001:8000
    env_file: .env
EOF
GITLAB_IP=$(dig +short git.knut.univention.de | tail -n1) docker compose build
docker compose up
```

You can test the API by running a test query:

```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/guardian/management/apps' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "kelvin-rest-api",
  "display_name": "Kelvin"
}'
```

### Running the tests

To run the tests locally on your machine follow these steps:

Prerequisites:
- Python 3.11 installed
- [Poetry 1.5.1](https://python-poetry.org/) installed

```shell
# pwd == $REPO_DIR/management-engine/guardian/management-api
poetry shell  # Or any other way to activate your virtual env for this project
poetry install
pytest -vv --cov=guardian_management_api .
```
