#!/bin/bash

# Copyright (C) 2024 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

print_help () {
  cat << EOF
usage: dev_run.sh COMMAND

This scripts runs commands in the development container.
If COMMAND is 'task', special, more complicated tasks can be run.

usage: dev_run.sh task TASK

The following tasks are available:

clean: Cleans up cached files and removes docker containers and local images.
build-image: Builds the docker image with the `no-cache` option.
dev-server: Starts the dev server including the frontend and the APIs.
dev-server-postgres: Same as dev-server, but with a postgresql database
sphinx: Starts the live server for the manual.
EOF
}

run_task() {
  TASK=$2
  if [ -z "$TASK" ]; then
    print_help
    exit 1
  fi
  echo "Running task $TASK"
  if [ "$TASK" = "clean" ]; then
    rm -rf .cache management-ui/node_modules
    DOCKER_USER=$DOCKER_USER GITLAB_IP=$GITLAB_IP docker compose \
    -f dev/docker-compose.yaml \
    -f dev/docker-compose-postgres.yaml \
    --profile "clean-profile" \
    down \
    --remove-orphans \
    --rmi local \
    --volumes
    exit $?
  fi
  if [ "$TASK" = "build-image" ]; then
    docker build -t guardian-dev:latest --no-cache -f dev/Dockerfile .
    exit $?
  fi
  if [ "$TASK" = "dev-server" ] || [ "$TASK" = "sphinx" ]; then
    DOCKER_USER=$DOCKER_USER GITLAB_IP=$GITLAB_IP docker compose \
    -f dev/docker-compose.yaml \
    --profile "$TASK" \
    up \
    --build
    exit $?
  fi
  if [ "$TASK" = "dev-server-postgres" ]; then
    DOCKER_USER=$DOCKER_USER GITLAB_IP=$GITLAB_IP docker compose \
    -f dev/docker-compose.yaml \
    -f dev/docker-compose-postgres.yaml \
    --profile "dev-server" \
    up \
    --build
    exit $?
  fi
  echo "Task '$TASK' does not exist."
  exit 1
}

run_command () {
  if [ -z "$COMMAND" ]; then
    print_help
    exit 1
  fi
  DOCKER_USER=$DOCKER_USER GITLAB_IP=$GITLAB_IP docker compose \
  -f dev/docker-compose.yaml \
  run \
  --build \
  --rm \
  -T \
  run_command "$@"
  exit $?
}

COMMAND="$1"
GITLAB_IP="$(getent -i ahostsv4 git.knut.univention.de | head -n 1 | cut -d ' ' -f 1)"
DOCKER_USER="$(id -u):$(id -g)"

if [ ! -f "dev/.env" ]; then
    cp dev/.env.example dev/.env
fi

if [ "$COMMAND" = "task" ]; then
  run_task $@
fi
if [ "$COMMAND" = "--help" ]; then
  print_help
  exit 0
else
  run_command $@
fi
