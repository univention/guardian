<!--
Copyright (C) 2023 Univention GmbH

SPDX-License-Identifier: AGPL-3.0-only
-->

# Guardian OPA Service

This is the docker container for the Guardian OPA service.
Right now it is very simple and starts the server on port 8181
with the integrated BaseBundle and no way to extend it with external
rego code. This has to be added at a later point.

## Starting the container

```shell
# pwd == $REPO_DIR/authorization-engine/guardian/opa
docker build -t guardian-opa:dev .
docker run --rm -p 8181:8181  guardian-opa:dev
```

## Running the OPA server locally

```shell
opa run --disable-telemetry --server --addr 0.0.0.0:8181 -l debug -b opa/BaseBundle
```

### Querying the OPA server

To query the `get_permissions` policy:

```shell
curl -s localhost:8181/v1/data/univention/base/get_permissions -d '{"input": {
                "actor": {
                        "id": "actor_id_1",
                        "roles": ["ucsschool:users:teacher"]
                },
                "targets": [{
                        "old": {"id": "target_id_1"},
                        "new": {"id": "target_id_1"}
                }],
                "namespaces": {"ucsschool": ["users", "groups"]},
                "contexts": {},
                "extra_args": {}
        }}'  -H 'Content-Type: application/json' | jq .
```

## Running the tests

```shell
opa test -b opa/BaseBundle -v
```

## Formatting the code

```shell
opa fmt -w opa/BaseBundle
```
