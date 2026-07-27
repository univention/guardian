#!/bin/sh
# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

# Docker accepts forwarded traffic to a published container port from any
# interface, so binding to 127.0.0.1 alone does not keep the LAN out.
# Only the guardian network itself may reach Cerbos.

set -e

if ! iptables -n -L DOCKER-USER >/dev/null 2>&1; then
	echo "no DOCKER-USER chain, leaving Cerbos reachable from the LAN" >&2
	exit 0
fi

iptables -C DOCKER-USER ! -i br-guardian -o br-guardian -j DROP 2>/dev/null ||
	iptables -I DOCKER-USER ! -i br-guardian -o br-guardian -j DROP
