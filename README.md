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

The Guardian manual can be found [here](https://docs.software-univention.de/guardian-manual/latest/index.html).

## Development

### Prerequisites

To develop the Guardian you just need [docker](https://www.docker.com/).
Installation instructions for Ubuntu can be found [here](https://docs.docker.com/engine/install/ubuntu/).

### Running commands in the development container

This repository provides a script, which allows you to run commands within a docker container,
that has all development tools preinstalled.

You can run any command `COMMAND` by executing

```shell
dev/dev_run.sh COMMAND
```

To run all pre-commit hooks for example, just execute

```shell
dev/dev_run.sh pre-commit run -a
```

### Use pre-commit

You can run pre-commit by executing the following command:

```shell
dev/dev_run.sh pre-commit run
```

Normally you use pre-commit by installing [pre-commit](https://pre-commit.com/) on your local machine
and running `pre-commit install` to install the pre-commit hook into the repository.
If you provide all the requirements, e.g. `python`, `nodejs`, `yarn`, etc. you can do so.

Alternatively you can use the following pre-commit hook, to execute pre-commit within docker,
so you do not need to install anything (other than docker) on your machine:

```shell
cat > .git/hooks/pre-commit << EOF
#!/bin/bash
dev/dev_run.sh pre-commit run
EOF
chmod +x .git/hooks/pre-commit
```

### Special tasks

The `dev_run` script provides some special tasks, which combine multiple or very long commands in one.
The available tasks are documented on the scripts help page, which can be accessed with:

```shell
dev/dev_run.sh --help
```

To run a task `TASK`, just execute:

```shell
dev/dev_run.sh task TASK
```

Some of those tasks are described in more detail here:

#### Start development server

To start the development server you have to execute the [dev_run.sh script](dev/dev_run.sh):

```shell
dev/dev_run.sh task dev-server
```

For the environment to work properly, your browser needs to be able to resolve
the hostname `guardian-proxy` to `localhost`.
One way to achieve this, would be to add the following line to your `/etc/hosts` file:

```text
127.0.0.1    guardian-proxy
```

The following services are available then:

- [Guardian Management API](http://guardian-proxy/guardian/management/docs)
  - development user credentials: `dev:univention`
- [Guardian Authorization API](http://guardian-proxy/guardian/authorization/docs)
- [Keycloak Admin console](http://guardian-proxy/keycloak/admin)
  - administrative credentials are: `admin:admin`

Both UI and APIs react to code changes without the need to restart the environment.

#### Cleanup the environment

Running the different services and jobs creates some artifacts:

- The `.cache` folder
- `node_modules` in [management-ui](management-ui)
- various docker containers, images and networks as part of the [docker compose setup](dev/docker-compose.yaml)

You can clean all of it by running:

```shell
dev/dev_run.sh task clean
```

#### Rebuild the docker image

All tasks and jobs are run within a special docker image, which contains all development dependencies.
When a task or command is executed, the image is build automatically.
If you want to force a fresh build without the docker build cache,
you can do so with the `build-image` task:

```shell
dev/dev_run.sh task build-image
```

#### Start live server for the manual

```shell
dev/dev_run.sh task sphinx
```

The manual can then be accessed at [http://localhost:8080/](http://localhost:8080/)

The port can be modified with the envar `SPHINX_PORT` in the `.env` file.
