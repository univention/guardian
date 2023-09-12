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

A local development environment is described [here](../README.md).

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

### Using the cli

This example shows you how to use the adapters on the cli.

First get into the container:

```shell
docker exec -ti management-guardian-dev /bin/bash
cd management-api/
# Optional: install ipython or just use python
poetry add ipython
ipython
# Alternative
python -m asyncio
```

I'm using a persistance adapter as an example:

```python
from guardian_management_api.ports.condition import ConditionPersistencePort
from guardian_management_api.models.condition import Condition
from guardian_management_api.adapter_registry import configure_registry, initialize_adapters
from guardian_lib.adapter_registry import ADAPTER_REGISTRY
from guardian_lib.adapter_registry import port_dep

configure_registry(ADAPTER_REGISTRY)
await initialize_adapters(ADAPTER_REGISTRY)
persistance_condition_adapter = await port_dep(ConditionPersistencePort)()
my_condition = Condition(name="my_condition", app_name="foo", namespace_name="bar", code=b"123")
await persistance_condition_adapter.create(my_condition)
```

## Notes for future documentation

### Bundle Server

The bundle server runs asynchronously to the API and generates the policy and data bundles for OPA.
It is important to note, that if a client to the API ingests faulty rego code, the bundle generation
will fail. As a consequence the last successfully built bundle before the faulty code was ingested, is served.

There is no direct feedback to whoever calls the API. In the future we might want to include something
like a healthcheck or similar. For now though the only way to identify a problem with the bundle build is to
observe the logs.
