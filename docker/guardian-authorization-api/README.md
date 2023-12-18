<!--
Copyright (C) 2023 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

# Guardian Authorization API

## Configuration

The app can be configured through the chosen adapter for the SettingsPort.

### Adapter settings

These settings are the only settings, that are always configured by providing environment variables instead of utilizing the SettingsPort.
These settings are also all required, and do not have any default value!

**GUARDIAN__AUTHZ__ADAPTER__SETTINGS_PORT,type=string**: Defines which adapter should be used for the settings port.
The project itself provides the `env` adapter, which can be used.

**GUARDIAN__AUTHZ__ADAPTER__PERSISTENCE_PORT,type=string** Defines which adapter should be used for the persistence port.

**GUARDIAN__AUTHZ__ADAPTER__POLICY_PORT,type=string** Defines which adapter should be used for the policy port.
The project itself provides the `opa` adapter, which can be used.

### Logging

**guardian.authz.logging.structured,type=bool,default=False**: If set to True, the logging output is structured as a JSON object

**guardian.authz.logging.level,type=Enum,default=SUCCESS**: Sets the log level of the application. The choices are DEBUG, INFO,
WARNING, ERROR, CRITICAL.

**guardian.authz.logging.format,type=string**: Defines the format of the log output, if not structured. The possible options are
described [here](https://loguru.readthedocs.io/en/stable/api/logger.html). The default is
`<green>{time:YYYY-MM-DD HH:mm:ss.SSS ZZ}</green> | <level>{level}</level> | <level>{message}</level> | {extra}`

**guardian.authz.logging.backtrace,type=bool,default=False**: Whether the exception trace formatted should be
extended upward, beyond the catching point, to show the full stacktrace which generated the error.

**guardian.authz.logging.diagnose,type=bool,default=False**: Whether the exception trace should display the variables
values to eases the debugging. This should be set to False in production to avoid leaking sensitive data.

## Adapters

The Guardian Authorization API provides some adapters, which are documented here

### EnvSettingsAdapter

**name**: env
**implements**: SettingsPort

The `EnvSettingsAdapter` loads settings exclusively from the environment. To find the correct environment variable
the setting name, e.g. *some.nested.important-option* is converted to uppercase and all dots are replace with double
underscores: *SOME__NESTED__IMPORTANT-OPTION*

### UDMPersistenceAdapter

**name** udm_data
**implements** PersistencePort

The `UDMPersistenceAdapter` loads the persistent data from a UDM REST API. It requires the following settings:

- `udm_data_adapter.url`: The URL of the UDM REST API
- `udm_data.username`: The username as which to connect to the REST API
- `udm_data.password`: The password for the login to the UDM REST API

### OPAAdapter

**name**: opa
**implements**: PolicyAdapter

The `OPAAdapter` queries an OPA service to return policy decisions.

It requires the setting `opa_adapter.url`, which should point to the running OPA instance to query.

## Local development

### Running the Guardian Authorization API locally

A local development environment is described [here](../README.md).

You can test the API by running a test query:

```shell
curl -X 'POST' \
  'http://localhost:8000/permissions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "actor": {
    "id": "my actor",
    "roles": [
      {
        "app_name": "string",
        "namespace_name": "string",
        "name": "string"
      }
    ],
    "attributes": {}
  },
  "include_general_permissions": false,
  "extra_request_data": {},
  "targets": [
    {
      "old_target": {"id": "target1", "roles": [], "attributes": []},
      "new_target": {"id": "target1", "roles": [], "attributes": []}
    }
  ]
}'
```

### Running the tests

To run the tests locally on your machine follow these steps:

Prerequisites:

- Python 3.11 installed
- [Poetry 1.5.1](https://python-poetry.org/) installed

```shell
# pwd == $REPO_DIR/authorization-engine/guardian/authorization-api
poetry shell  # Or any other way to activate your virtual env for this project
poetry install
pytest -vv --cov=guardian_authorization_api .
```

There are also integration tests, that run automatically, if their prerequisites are met.

To be able to run the integration tests against the test mapping inside the authorization api docker container,
run the following commands in the project directory outside the docker container.

```shell
cp management-api/rego_policy_bundle_template/univention/test_mapping/data.json management_service_dir/bundle_server/build/GuardianDataBundle/guardian/mapping/data.json
opa build -b management_service_dir/bundle_server/build/GuardianDataBundle -o management_service_dir/bundle_server/bundles/GuardianDataBundle.tar.gz
```

You can enable or disable
the integration tests on purpose by using the `integration` mark:

```shell
#pwd == $REPO_DIR/authorization-engine/guardian/authorization-api
poetry shell  # Or any other way to activate your virtual env for this project
poetry install
pytest -vv -m integration .  # Runs integration tests only
pytest -vv --cov=guardian_authorization_api -m "not integration" .  # Never runs integration tests
```

#### UDMPersistenceAdapter integration tests

The integration tests for the `UDMPersistenceAdapter` require the settings for the adapter to be available in the env.
The UDM REST API it connects to is expected to be set up with [this Jenkins Job](https://univention-dist-jenkins.k8s.knut.univention.de/job/UCSschool-5.0/view/Environments/job/SchoolMultiserverEnvironment/)
