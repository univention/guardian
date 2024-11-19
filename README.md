<!--
Copyright (C) 2023 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

[![Renovate](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](../issues/?search=Dependency%20Dashboard)
[![Renovate](https://img.shields.io/badge/renovate-pipeline-brightgreen.svg)](../pipelines/new?var[RUN_RENOVATE]=yes)

# Guardian

This repository contains various components that make up the Guardian.

The Guardian is the main component of the UCS authorization engine and
contains the management of roles, permissions, etc. (Guardian Management API) as well as the API for
querying policy decisions (Guardian Authorization API). The Guardian allows to set up complex attribute based
access control (ABAC) and enables the integration with various UCS and third party components.

The Guardian manual can be found [here](https://docs.software-univention.de/guardian-manual/latest/index.html).

The Guardian developer reference is not yet published anywhere and has to be build locally.
This can be done by running:

```bash
docker run -ti --rm -v "$PWD:/project" -w /project -u $UID --network=host --pull always \
docker-registry.knut.univention.de/sphinx:latest \
make -C docs/developer-reference/ livehtml
```

It can now be accessed at http://localhost:8000

Some documentation was not yet migrated to the developer reference and can be found here:

- [Guardian Management API](management-api/README.md)
- [Guardian Authorization API](authorization-api/README.md)
- [OPA service](opa/README.md)

The information contained in those README files might be incomplete or faulty and should be migrated
to the developer reference as soon as possible.
