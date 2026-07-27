#!/bin/sh
# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

# The packetfilter rule matches on the bridge name, so a network with any other
# bridge would leave Cerbos open. Recreate it rather than leave it wrong.

set -e

NETWORK='guardian'
BRIDGE='br-guardian'

if docker network inspect "$NETWORK" >/dev/null 2>&1; then
	current="$(docker network inspect -f '{{index .Options "com.docker.network.bridge.name"}}' "$NETWORK")"
	if [ "$current" = "$BRIDGE" ]; then
		exit 0
	fi
	# Attached containers keep the network alive. They reach Cerbos again once
	# they reconnect, which they do when restarted.
	for container in $(docker network inspect -f '{{range .Containers}}{{.Name}} {{end}}' "$NETWORK"); do
		echo "detaching $container to rebuild $NETWORK on $BRIDGE; restart it afterwards" >&2
		docker network disconnect -f "$NETWORK" "$container"
	done
	docker network rm "$NETWORK"
fi

docker network create --driver bridge --opt "com.docker.network.bridge.name=$BRIDGE" "$NETWORK"
