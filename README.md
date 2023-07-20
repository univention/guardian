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

## Development

Most information regarding development and setup of local environments can be found in the component sub folders.

### Shared dependencies

The projects in this repository have a couple of dependencies, they have in common. For effective local development
you should make sure that those are met:

- [Python 3.11](https://www.python.org/downloads/release/python-3114/)
- [Poetry](https://python-poetry.org/) in version 1.5.1
- [pre-commit](https://pre-commit.com/) in version 3.3.3
- [Docker](https://www.docker.com/) with support of [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [OPA](https://www.openpolicyagent.org/) in version 0.53.0

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
