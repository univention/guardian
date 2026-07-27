#!/usr/share/ucs-test/runner pytest-3 -s -l -vv
## desc: Guardian Cerbos endpoint reachable through guardian/cerbos/url
## tags: [guardian]
## exposure: safe
## packages:
##   - univention-guardian-server

# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

"""One URL, two deployment shapes.

guardian/cerbos/url must work for a native host process and, unchanged, for a
container on the shared 'guardian' network. Nothing off that network may reach
Cerbos, which is unauthenticated.
"""

import os
import subprocess
from urllib.parse import urlsplit

import pytest
import requests

from univention.config_registry import ucr


# Services discover the endpoint through this one variable, so the tests do too.
CERBOS_BASE_URL = os.environ.get('CERBOS_BASE_URL') or ucr.get('guardian/cerbos/url', '')
CERBOS_HOST = os.environ.get('CERBOS_HOST') or urlsplit(CERBOS_BASE_URL).netloc

DOCKER = '/usr/bin/docker'
NETWORK = 'guardian'
BRIDGE = 'br-guardian'
CONTAINER = 'cerbos'
PORT = CERBOS_HOST.rsplit(':', 1)[-1]


def _docker(*args):
    return subprocess.run([DOCKER, *args], capture_output=True, text=True)


def _healthcheck(image, host_port, *docker_args):
    """Probe host_port from a throwaway container built on the Cerbos image.

    `-e CERBOS_CONFIG` unsets the image default, which excludes --host-port.
    """
    return _docker(
        'run',
        '--rm',
        *docker_args,
        '-e',
        'CERBOS_CONFIG',
        image,
        'healthcheck',
        '--kind=http',
        f'--host-port={host_port}',
        '--no-tls',
    )


@pytest.fixture(scope='module')
def cerbos_image() -> str:
    """Image of the running Cerbos container, already pulled by the package."""
    res = _docker('inspect', '--format', '{{.Config.Image}}', CONTAINER)
    if res.returncode != 0:
        pytest.skip(f'{CONTAINER} container not running: {res.stderr.strip()}')
    return res.stdout.strip()


@pytest.fixture(scope='module')
def cerbos_ip() -> str:
    """Address of the Cerbos container on the shared network."""
    res = _docker('inspect', '--format', f'{{{{.NetworkSettings.Networks.{NETWORK}.IPAddress}}}}', CONTAINER)
    assert res.returncode == 0, res.stderr
    ip = res.stdout.strip()
    assert ip, f'{CONTAINER} has no address on {NETWORK}'
    return ip


def test_ucr_url_serves_policy_decisions():
    """The discovery variable is set and its URL reaches a working PDP."""
    assert CERBOS_BASE_URL, 'guardian/cerbos/url is not set'
    payload = {
        'principal': {'id': 'alice', 'roles': ['user']},
        'resources': [{'resource': {'id': 'r-1', 'kind': 'document'}, 'actions': ['view']}],
    }
    resp = requests.post(f'{CERBOS_BASE_URL}/api/check/resources', json=payload, timeout=10)
    resp.raise_for_status()
    assert resp.json()['results'][0]['actions']['view'] == 'EFFECT_ALLOW'


def test_same_url_reachable_from_a_container(cerbos_image):
    """A container on the shared network reaches Cerbos by the very same URL."""
    res = _healthcheck(cerbos_image, CERBOS_HOST, '--network', NETWORK)
    assert res.returncode == 0, res.stderr or res.stdout
    assert 'SERVING' in res.stdout, res.stdout


def test_network_uses_the_fixed_bridge_name():
    """The packetfilter rule matches on the bridge name, so it must be fixed."""
    res = _docker(
        'network',
        'inspect',
        '--format',
        '{{index .Options "com.docker.network.bridge.name"}}',
        NETWORK,
    )
    assert res.stdout.strip() == BRIDGE, res.stdout or res.stderr


def test_unreachable_by_name_off_the_network(cerbos_image):
    """Off the shared network the name does not resolve."""
    res = _healthcheck(cerbos_image, CERBOS_HOST)
    assert res.returncode != 0, res.stdout


def test_unreachable_by_address_from_another_network(cerbos_image, cerbos_ip):
    """Nor by address from another Docker network, which Docker itself isolates."""
    res = _healthcheck(cerbos_image, f'{cerbos_ip}:{PORT}')
    assert res.returncode != 0, res.stdout


def test_lan_ingress_to_the_bridge_is_dropped():
    """Docker forwards LAN traffic to a published port; this rule is what stops it.

    Only its presence is checked - exercising the path needs a client outside
    this host's networking, which Docker's own isolation does not stand in for.
    """
    res = subprocess.run(
        ['/usr/sbin/iptables', '-C', 'DOCKER-USER', '!', '-i', BRIDGE, '-o', BRIDGE, '-j', 'DROP'],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stderr or res.stdout
