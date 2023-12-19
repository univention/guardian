<!--
Copyright (C) 2023 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

# Guardian

This repository contains various components that make up the Guardian.

The Guardian is the main component of the UCS authorization engine and
contains the management of roles, permissions, etc. (Guardian Management API) as well as the API for
querying policy decisions (Guardian Authorization API). The Guardian allows to set up complex attribute based
access control (ABAC) and enables the integration with various UCS and third party components.

## Components

### Guardian Authorization API

This is the API to query for policy decisions. It relies on the Open Policy Agent, which is
implemented in [opa](opa/README.md).

More information can be found [here](authorization-api/README.md).

### Guardian Management API

This is the API to manage objects of the Guardian. This includes roles, namespaces, apps, permissions, etc.

More information can be found [here](management-api/README.md)

### OPA service

The Guardian Authorization API relies on an Open Policy Agent. An implementation is provided in this repository.

More information can be found [here](opa/README.md)

## Apps

### Guardian Authorization API

This app contains the components `Guardian Authorization API` and the OPA service in a docker compose app.
The configuration files can be found in `appcenter-authz`. The App ID is `guardian-authorization-api`.

This app can be installed via `univention-app install guardian-authorization-api`. It depends on having
Keycloak and the Guardian Management API installed in the domain.

To work properly it also requires the UDM connection settings on installation time. This is not automated (yet).
If installed via the UMC, you are prompted to enter them before installation. If you use the terminal:

```shell
univention-app configure guardian-authorization-api \
  --set guardian-authorization-api/udm_data/url=$URL \
  guardian-authorization-api/bundle_server_url=https://$URL_TO_MANAGEMENT_API
```

### Guardian Management API

This app contains the components for `Guardian Management API`.
The configuration files can be found in `appcenter-management`. The App ID is `guardian-management-api`.

This app can be installed via `univention-app install guardian-management-api`. It depends on having
Keycloak installed in the domain.

If you use the `GuardianAuthorizationAdapter` you should use Keycloak on a real UCS system. This is required for some integration tests, such as `TestGuardianAuthorizationAdapterIntegration`, for those tests to not be skipped, the environment variable `UCS_HOST_IP` needs to be set. Then, on your UDM machine, create a user to manage the `guardian` app:

```bash
udm users/user create \
  --set username=guardian \
  --set lastname=app-admin \
  --set password=univention \
  --set guardianRole=guardian:builtin:app-admin \
  --position cn=users,$(ucr get ldap/base)
```

For Keycloak to have the right configuration, install the Guardian apps from the App Center or manually copy the client
configuration from the `dev-compose.yml` Keycloak container.

You will need to fetch the `guardian-management-api` client secret from Keycloak and set it in the `.env` for development
(`OAUTH_ADAPTER__M2M_SECRET`).

Additionally, if you don't use `dev-run` and instead run `docker compose up` directly, the variable `UCS_HOST_IP` needs to be set:

```shell
source .env
```

By default, if started with `dev-compose.yml`, the Authorization API service will be used directly. But when installed from the App Center, it needs to be configured through the app setting `guardian-management-api/authorization_api_url` which sets the environment variable `GUARDIAN__MANAGEMENT__ADAPTER__AUTHORIZATION_API_URL`.

### Guardian Management UI

This app contains the frontend of the Guardian.
Currently, this is not yet in the app center.

Please see the README in `management-ui` for more information.

## Development

The first step is to create a copy of the example env file and adapt it to your environment.

```shell
cp .env.example .env
#  Edit .env
#  If you want to run it outside docker, you need to source it
source .env
```

Start the dev environment:

```shell
./dev-run
```

You get both APIs up and running on port 80, including live reload when editing your local files.

You also get a build of the [Guardian Management UI](#guardian-management-ui) running on port 80
(Served under http://localhost/univention/guardian/management-ui/). Note: That container is a static compiled build of the frontend.
To develop the frontend see the README in `management-ui`.

_Note: docker compose uses the environment variables from `.env` by default._
_Make sure the contents of it are correct or pass `--env-file .env.example` to_
_use the default values._

You might need to install the docker compose plugin.
Either use the [official docker repositories](https://docs.docker.com/compose/install/linux/#install-using-the-repository) to install docker.
Or [download the plugin manually](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually).

You can now access the following services:

- [authorization-api](http://localhost/guardian/authorization/docs/)
- [management-api](http://localhost/guardian/management/docs/)
- [management-ui](http://localhost/univention/guardian/management-ui/)

Secondary services for integration:

- [keycloak](http://traefik/guardian/keycloak/)

### Documentation

To run the liveserver for developing the documentation run the following command in the
guardian repository's root:

```shell
docker run -ti --rm -v "$PWD:/project" -w /project -u $UID --network=host --pull always \
docker-registry.knut.univention.de/sphinx:latest \
make -C docs/guardian-manual/ livehtml
```

### Authentication

You can choose between multiple authentication providers.
Set them in `GUARDIAN__AUTHZ__ADAPTER__AUTHENTICATION_PORT` and `GUARDIAN__MANAGEMENT__ADAPTER__AUTHENTICATION_PORT`.

- `fast_api_always_authorized`
- `fast_api_never_authorized`
- `fast_api_oauth`

If you choose `fast_api_oauth` the local keycloak started in the compose file will be used.
The username is `dev:univention`. The admin credentials for keycloak are `admin:admin`.

*Note: If you want to use the keycloak supplied by the docker compose file,
you need to add traefik to your /etc/hosts file: `127.0.0.1 traefik`.*

You can use your own keycloak by changing `OAUTH_ADAPTER__WELL_KNOWN_URL`.
You might need to change `SSL_CERT_FILE` and provide a cert file.

### CORS

If you run into CORS errors while testing a UI, you should enable the following
settings in your `.env` file:

```shell
export GUARDIAN__AUTHZ__CORS__ALLOWED_ORIGINS=*
export GUARDIAN__MANAGEMENT__CORS__ALLOWED_ORIGINS=*
```

If you don't want to allow all (`*`), change it to a comma-separated list of
hosts that you would like to use, without spaces.

### Shared dependencies

The projects in this repository have a couple of dependencies, they have in common. For effective local development
you should make sure that those are met:

- [Python 3.11](https://www.python.org/downloads/release/python-3114/)
- [Poetry](https://python-poetry.org/) in version 1.5.1
- [pre-commit](https://pre-commit.com/) in version 3.3.3
- [Docker](https://www.docker.com/) with support of [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [OPA](https://www.openpolicyagent.org/) in version 0.53.0
- [Regal](https://github.com/StyraInc/regal) OPA linter in version 0.8.0

### Licensing information

License information is added to source files via [REUSE](https://reuse.software/). License information can be added
like this:

```shell
# pwd == $REPO_DIR/authorization-engine/guardian/
# Activate your preferred python env
pip install reuse
reuse annotate \
--copyright="Univention GmbH" \
--license="AGPL-3.0-only" \
--copyright-style="string-c" \
--template=univention \
--year "2023" \
--recursive \
--merge-copyrights \
--skip-unrecognised \
--skip-existing \
.
```
