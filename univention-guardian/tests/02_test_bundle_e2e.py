#!/usr/share/ucs-test/runner pytest-3 -s -l -vv
## desc: Cerbos policy bundle listener end-to-end (register -> disk -> restart -> serve)
## tags: [guardian]
## exposure: dangerous
## roles: [domaincontroller_master]
## packages:
##   - univention-guardian-server

# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

"""End-to-end tests for the cerbos-policies listener.

Register a guardian/policy-bundle via ucs_registerLDAPExtension and verify the
listener extracts it into POLICIES_DIR/<app>/, validates it with cerbos compile,
restarts Cerbos, and Cerbos then serves it.
"""

import io
import json
import os
import shlex
import subprocess
import tarfile
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

import pytest
import requests

from univention.config_registry import ucr


CERBOS_BASE_URL = 'http://127.0.0.1:3592'
POLICIES_DIR = Path('/usr/share/univention-guardian-server/policies')
APP_POLICIES_DIR = POLICIES_DIR / 'ucstest_e2e'
E2E_TIMEOUT = 60.0
LISTENER_LOG = '/var/log/univention/listener.log'
VALID_POLICY = """\
apiVersion: api.cerbos.dev/v1
resourcePolicy:
  resource: ucstest.e2e.resource
  version: default
  rules:
    - actions: ["view"]
      effect: EFFECT_ALLOW
      roles: [tester]
"""
INVALID_POLICY = """\
apiVersion: api.cerbos.dev/v1
resourcePolicy:
  resource: ucstest.e2e.resource
  version: default
  importDerivedRoles: [does_not_exist]
  rules:
    - actions: ["view"]
      effect: EFFECT_ALLOW
      derivedRoles: [does_not_exist]
"""


def poll(predicate: Callable[[], bool], *, timeout: float = E2E_TIMEOUT, interval: float = 2.0) -> bool:
    """Call ``predicate`` every ``interval`` seconds until it is true or ``timeout`` elapses."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return bool(predicate())


def cerbos_decision(roles=('tester',)) -> str:
    """Ask Cerbos whether `roles` may 'view' the test resource.

    Returns the effect ('EFFECT_ALLOW' or 'EFFECT_DENY'), or '' while Cerbos is
    unreachable (which happens during the restart).
    """
    payload = {
        'principal': {'id': 'alice', 'roles': list(roles)},
        'resources': [{'resource': {'id': 'r1', 'kind': 'ucstest.e2e.resource'}, 'actions': ['view']}],
    }
    try:
        resp = requests.post(f'{CERBOS_BASE_URL}/api/check/resources', json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()['results'][0]['actions']['view']
    except requests.RequestException:
        return ''


def cerbos_serving() -> bool:
    """True if the Cerbos health endpoint reports SERVING."""
    try:
        resp = requests.get(f'{CERBOS_BASE_URL}/_cerbos/health', timeout=5)
    except requests.RequestException:
        return False
    if not resp.ok:
        return False
    try:
        return resp.json().get('status') == 'SERVING'
    except ValueError:
        return False


def register_bundle(policy_text: str) -> None:
    """Register the test bundle (one resource policy) via ucs_registerLDAPExtension.

    ucs_registerLDAPExtension bz2-compresses the payload and the listener
    bz2-decompresses it, so the bundle content is a plain (uncompressed) tar.
    """
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w') as tar:
        data = policy_text.encode('utf-8')
        info = tarfile.TarInfo('resource_policies/e2e.yaml')
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))

    with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as fh:
        fh.write(buf.getvalue())
        tar_path = fh.name
    try:
        base = ucr['ldap/base']
        meta = json.dumps({'app': 'ucstest_e2e', 'version': '1'})
        cmd = (
            '. /usr/share/univention-lib/all.sh && '
            'ucs_registerLDAPExtension '
            '--packagename ucs-test-guardian '
            '--packageversion 1 '
            '--name guardian-policy-bundle-ucstest-e2e '
            f'--data {shlex.quote(tar_path)} '
            f'--data_meta {shlex.quote(meta)} '
            '--data_type guardian/policy-bundle '
            f'--binddn cn=admin,{base} --bindpwdfile /etc/ldap.secret'
        )
        subprocess.run(['/usr/bin/bash', '-c', cmd], check=True)
    finally:
        os.unlink(tar_path)


def unregister_bundle() -> None:
    """Unregister the bundle via ucs_unregisterLDAPExtension (the counterpart to
    register_bundle, best effort). The listener then deletes the app directory
    and restarts Cerbos."""
    base = ucr['ldap/base']
    cmd = (
        '. /usr/share/univention-lib/all.sh && '
        'ucs_unregisterLDAPExtension --data guardian-policy-bundle-ucstest-e2e '
        f'--binddn cn=admin,{base} --bindpwdfile /etc/ldap.secret'
    )
    subprocess.run(['/usr/bin/bash', '-c', cmd], check=False)


@pytest.fixture
def clean_bundle():
    """Pre-clean any leftover bundle, and guarantee teardown after the test.

    Removes any object left by an earlier run first; on teardown (even on
    failure) removes the object and waits for the app policy directory to
    disappear and Cerbos to be healthy again (the removal also triggers a
    restart).
    """
    unregister_bundle()
    assert poll(lambda: cerbos_decision() == 'EFFECT_DENY'), (
        'test resource decidable before registration (leftover state?)'
    )
    try:
        yield
    finally:
        unregister_bundle()
        poll(lambda: cerbos_serving() and not APP_POLICIES_DIR.exists())


def test_e2e_valid_bundle_is_applied(clean_bundle):
    """A registered bundle is written to disk, activated, and served."""
    register_bundle(VALID_POLICY)

    # 1. the listener writes the tree
    assert poll(lambda: (APP_POLICIES_DIR / 'resource_policies' / 'e2e.yaml').is_file()), (
        f'listener did not write the bundle to {APP_POLICIES_DIR}'
    )

    # 2. ownership matches the Cerbos container user (64110:64110)
    st = APP_POLICIES_DIR.stat()
    assert (st.st_uid, st.st_gid) == (64110, 64110), (
        f'app policy dir owned by {st.st_uid}:{st.st_gid}, expected 64110:64110'
    )

    # 3. Cerbos restarts and serves the policy
    assert poll(lambda: cerbos_decision() == 'EFFECT_ALLOW'), 'Cerbos did not serve the policy after registration'

    # 4. not over-permissive: an unrelated role is denied
    assert cerbos_decision(roles=['nobody']) == 'EFFECT_DENY'


def test_e2e_invalid_bundle_is_rejected(clean_bundle):
    """A bundle that fails cerbos compile is rolled back and never served."""
    log_offset = os.path.getsize(LISTENER_LOG) if os.path.exists(LISTENER_LOG) else 0

    register_bundle(INVALID_POLICY)

    def rejection_logged() -> bool:
        try:
            with open(LISTENER_LOG, encoding='utf-8', errors='replace') as fh:
                fh.seek(log_offset)
                return any('rejected invalid policy bundle' in line and 'ucstest_e2e' in line for line in fh)
        except OSError:
            return False

    assert poll(rejection_logged), 'listener did not log a rejection for ucstest_e2e'
    assert not APP_POLICIES_DIR.exists(), 'invalid bundle left files on disk (rollback failed)'
    assert cerbos_decision() == 'EFFECT_DENY', 'invalid bundle became decidable'
