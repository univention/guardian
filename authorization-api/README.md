# Guardian Authorization API

## Configuration

The app can be fully configured with env variables.

### Logging

**GUARDIAN_AUTHZ_LOGGING_STRUCTURED,type=bool,default=False**: If set to True, the logging output is structured as a JSON object

**GUARDIAN_AUTHZ_LOGGING_LEVEL,type=Enum,default=SUCCESS**: Sets the log level of the application. The choices are TRACE, DEBUG, INFO,
SUCCESS, WARNING, ERROR, CRITICAL.

**GUARDIAN_AUTHZ_LOGGING_LOG_FORMAT,type=string**: Defines the format of the log output, if not structured. The possible options are
described [here](https://loguru.readthedocs.io/en/stable/api/logger.html). The default is
`<green>{time:YYYY-MM-DD HH:mm:ss.SSS ZZ}</green> | <level>{level}</level> | <level>{message}</level> | {extra}`

### Adapter settings

These settings are all required, and do not have any default value!

**GUARDIAN_AUTHZ_ADAPTER_SETTINGS_PORT,type=string**: Defines which adapter should be used for the settings port.
The project itself provides the `env` adapter, which can be used.

**GUARDIAN_AUTHZ_ADAPTER_PERSISTENCE_PORT,type=string** Defines which adapter should be used for the persistence port.
The project itself provides the `static_data` adapter, which can be used.

## Adapters

The Guardian Authorization API provides some adapters, which are documented here

### EnvSettingsAdapter

**name**: env
**implements**: SettingsPort

The `EnvSettingsAdapter` loads settings exclusively from the environment. To find the correct environment variable
the setting name, e.g. *some.nested.important-option* is converted to uppercase and all dots are replace with double
underscores: *SOME__NESTED__IMPORTANT-OPTION*

### StaticDataAdapter

**name**: static_data
**implements**: PersistencePort

The `StaticDataAdapter` loads the persistent data from a json file. This adapter is very rudimentary and not suitable for
production!

It requires the setting `static_data_adapter.data_file` to point to a JSON file containing the data. It needs to have
a format like this:

```json
{
  "users": {
      "USER1": {"attributes": {"A": 1, "B": 2}},
      "USER2": {"attributes": {}}
  },
  "groups": {
      "GROUP1": {"attributes": {"C": 3, "D": 4}},
      "GROUP2": {"attributes": {"E": 5, "F": 6}}
  }
}
```

## Local development

### Running the Guardian Authorization API locally

To start the API on your local machine, follow these steps:

Prerequisites:

- Docker installed
- If run without docker:
  - Python 3.11 installed
  - [Poetry](https://python-poetry.org/) installed

```shell
# pwd == $REPO_DIR/authorization-engine/guardian/authorization-api
docker build -t guardian-authz:dev .
cat > .env << EOF
GUARDIAN_AUTHZ_LOGGING_LEVEL=DEBUG
GUARDIAN_AUTHZ_LOGGING_STRUCTURED=0
GUARDIAN_AUTHZ_ADAPTER_SETTINGS_PORT=env
GUARDIAN_AUTHZ_ADAPTER_PERSISTENCE_PORT=static_data
STATIC_DATA_ADAPTER__DATA_FILE=/guardian_service_dir/test_data.json
EOF
cat > test_data.json << EOF
{
  "users": {
      "USER1": {"attributes": {"A": 1, "B": 2}},
      "USER2": {"attributes": {}}
  },
  "groups": {
      "GROUP1": {"attributes": {"C": 3, "D": 4}},
      "GROUP2": {"attributes": {"E": 5, "F": 6}}
  }
}
EOF
docker run --rm -p 8000:8000 --env-file .env guardian-authz:dev
```

Alternatively you can start the service directly, without a docker container:

```shell
cat > .env << EOF
GUARDIAN_AUTHZ_LOGGING_LEVEL=DEBUG
GUARDIAN_AUTHZ_LOGGING_STRUCTURED=0
GUARDIAN_AUTHZ_ADAPTER_SETTINGS_PORT=env
GUARDIAN_AUTHZ_ADAPTER_PERSISTENCE_PORT=static_data
STATIC_DATA_ADAPTER__DATA_FILE=test_data.json
EOF
cat > test_data.json << EOF
{
  "users": {
      "USER1": {"attributes": {"A": 1, "B": 2}},
      "USER2": {"attributes": {}}
  },
  "groups": {
      "GROUP1": {"attributes": {"C": 3, "D": 4}},
      "GROUP2": {"attributes": {"E": 5, "F": 6}}
  }
}
EOF
poetry shell  # Or any other way to activate your virtual env for this project
poetry install
export $(xargs <.env)
gunicorn --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 guardian_authorization_api.main:app
```

### Running the tests

To run the tests locally on your machine follow these steps:

Prerequisites:
- Python 3.11 installed
- [Poetry](https://python-poetry.org/) installed

```shell
# pwd == $REPO_DIR/authorization-engine/guardian/authorization-api
poetry shell  # Or any other way to activate your virtual env for this project
poetry install
pytest -vv --cov=guardian_authorization_api .
```
