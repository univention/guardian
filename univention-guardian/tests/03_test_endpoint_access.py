#!/usr/share/ucs-test/runner pytest-3 -s -l -vv
## desc: Cerbos endpoint reachable from the host and from a container
## tags: [guardian]
## exposure: safe
## roles: [domaincontroller_master]
## packages:
##   - univention-guardian-server

# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

"""The two ways a service reaches Cerbos on UCS.

A native host process uses the published loopback port. A container cannot reach
that interface, so it joins the shared 'guardian' network and addresses Cerbos by
its DNS name instead.
"""

import subprocess

import requests


HOST_HEALTH_URL = 'http://127.0.0.1:3592/_cerbos/health'
DOCKER_NETWORK_HEALTH_URL = 'http://cerbos:3592/_cerbos/health'


def test_host_process_reaches_cerbos():
    """A native host process reaches the health endpoint on the published loopback port."""
    resp = requests.get(HOST_HEALTH_URL, timeout=10)
    resp.raise_for_status()
    assert resp.json()['status'] == 'SERVING', resp.text


def test_container_on_the_network_reaches_cerbos():
    """A container on the shared network reaches the health endpoint by DNS name."""
    cmd = ['/usr/bin/docker', 'run', '--rm', '--network', 'guardian', 'curlimages/curl:8.11.1']
    cmd += ['--fail-with-body', '-sS', DOCKER_NETWORK_HEALTH_URL]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr or res.stdout
    assert 'SERVING' in res.stdout, res.stdout
