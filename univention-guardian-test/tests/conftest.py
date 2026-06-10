# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

"""Shared fixtures and helpers. Talks to Cerbos at 127.0.0.1:3592; never starts or stops it."""

import os
import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, TypeVar

import pytest
from cerbos.sdk.client import CerbosClient
from cerbos.sdk.model import Principal, Resource, ResourceAction, ResourceList

CERBOS_HOST = os.environ.get("CERBOS_HOST", "http://127.0.0.1:3592")
POLICIES_DIR = Path(
    os.environ.get(
        "CERBOS_POLICIES_DIR", "/usr/share/univention-guardian-server/policies"
    )
)
SCRATCH_PREFIX = "pytest_scratch_"
RELOAD_TIMEOUT = float(os.environ.get("CERBOS_RELOAD_TIMEOUT", "5"))

T = TypeVar("T")


@pytest.fixture(scope="session")
def cerbos() -> CerbosClient:
    """Cerbos SDK client."""
    with CerbosClient(host=CERBOS_HOST) as client:
        yield client


@pytest.fixture
def scratch_dir() -> Path:
    """Yields POLICIES_DIR; drops all `pytest_scratch_*.yaml` files on teardown.

    Scratch files land directly in POLICIES_DIR, not a subdirectory.
    Cerbos only watches directories that exist at startup — new directories
    created at runtime are never added (processEvent drops directory events
    as non-indexable before triggerUpdate can call watcher.Add on them).
    """
    if os.geteuid() != 0:
        pytest.skip("hot-reload tests need write access to the policies dir")
    if not POLICIES_DIR.is_dir():
        pytest.skip(f"policies dir not found: {POLICIES_DIR}")

    for f in POLICIES_DIR.glob(f"{SCRATCH_PREFIX}*.yaml"):
        f.unlink(missing_ok=True)
    try:
        yield POLICIES_DIR
    finally:
        for f in POLICIES_DIR.glob(f"{SCRATCH_PREFIX}*.yaml"):
            f.unlink(missing_ok=True)
        time.sleep(1.0)


def wait_until(
    predicate: Callable[[], T],
    *,
    timeout: float = RELOAD_TIMEOUT,
    interval: float = 0.2,
    message: str | None = None,
) -> T:
    """Poll `predicate` every `interval` seconds until truthy or `timeout`. Returns the value."""
    deadline = time.monotonic() + timeout
    last: T | None = None
    while time.monotonic() < deadline:
        last = predicate()
        if last:
            return last
        time.sleep(interval)
    raise AssertionError(
        message or f"predicate did not become true within {timeout}s (last={last!r})"
    )


def check_actions(
    client: CerbosClient,
    *,
    roles: Iterable[str],
    kind: str,
    actions: Iterable[str],
    attr: dict[str, Any] | None = None,
    principal_id: str = "alice",
    principal_attr: dict[str, Any] | None = None,
    resource_id: str = "r-1",
) -> dict[str, str]:
    """One principal vs. one resource, N actions. Returns `{action: effect}`."""
    principal = Principal(
        id=principal_id,
        roles=set(roles),
        attr=principal_attr or {},
    )
    resource = Resource(id=resource_id, kind=kind, attr=attr or {})
    resp = client.check_resources(
        principal=principal,
        resources=ResourceList(
            resources=[ResourceAction(resource=resource, actions=set(actions))]
        ),
    ).raise_if_failed()
    return dict(resp.results[0].actions)
