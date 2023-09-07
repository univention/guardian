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

### Guardian Management API

This app contains the components for `Guardian Management API`.
The configuration files can be found in `appcenter-management`. The App ID is `guardian-management-api`.

### Guardian Management UI

This is a frontend app that is paired with the Guardian Management UI.
Currently this is not dockerized or in the app center. Please see the README
in `management-ui`.

## Development

The first step is to create a copy of the example env file and adapt it to your environment.

```shell
cp .env.example .env
#  Edit .env
#  If you want to run it outside docker, you need to source it
source .env
```

The second step is to create the directory for the bind mount in the docker compose file:

```shell
mkdir management_service_dir
```

This repository provides a dev-compose.yaml. If the docker environment is started
via

```shell
docker compose -f dev-compose.yaml build  # This should only be necessary once and if the docker files change
docker compose -f dev-compose.yaml up
```

you get both APIs up and running on port 80, including live reload when editing your local files.

_Note: docker compose uses the environment variables from `.env` by default._
_Make sure the contents of it are correct or pass `--env-file .env.example` to_
_use the default values._

You might need to install the docker compose plugin.
Either use the [official docker repositories](https://docs.docker.com/compose/install/linux/#install-using-the-repository) to install docker.
Or [download the plugin manually](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually).

Some of the services are configured to run with the UID 1000 to avoid creating files with root in your local
folder structure. If your current user does not have the UID 1000, remove the lines from the docker compose file.
It should work then, but you will have files in your local repo, which are owned by root.

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
