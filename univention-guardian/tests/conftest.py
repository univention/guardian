# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

"""Shared fixtures and helpers"""

import os
import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, Generator, TypeVar

import pytest
import requests

CERBOS_HOST = os.environ.get("CERBOS_HOST", "127.0.0.1:3592")
CERBOS_BASE_URL = os.environ.get("CERBOS_BASE_URL", f"http://{CERBOS_HOST}")
POLICIES_DIR = Path(
    os.environ.get(
        "CERBOS_POLICIES_DIR", "/usr/share/univention-guardian-server/policies"
    )
)
SCRATCH_PREFIX = "pytest_scratch_"
RELOAD_TIMEOUT = float(os.environ.get("CERBOS_RELOAD_TIMEOUT", "5"))

T = TypeVar("T")


@pytest.fixture(scope="session")
def cerbos() -> requests.Session:
    """HTTP session for the Cerbos REST API."""
    with requests.Session() as session:
        yield session


@pytest.fixture
def scratch_dir() -> Generator[Path]:
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


def check_resources(
    session: requests.Session,
    *,
    roles: Iterable[str],
    resources: list[dict[str, Any]],
    principal_id: str = "alice",
    principal_attr: dict[str, Any] | None = None,
) -> dict[str, dict[str, str]]:
    """Returns `{resource_id: {action: "EFFECT_ALLOW"|"EFFECT_DENY"}}`.

    Each resource dict: ``{"id": str, "kind": str, "actions": list[str], "attr": dict}``
    """
    payload = {
        "principal": {
            "id": principal_id,
            "roles": list(roles),
            "attr": principal_attr or {},
        },
        "resources": [
            {
                "resource": {
                    "id": r["id"],
                    "kind": r["kind"],
                    "attr": r.get("attr") or {},
                },
                "actions": list(r["actions"]),
            }
            for r in resources
        ],
    }
    resp = session.post(
        f"{CERBOS_BASE_URL}/api/check/resources", json=payload, timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        result["resource"]["id"]: dict(result.get("actions", {}))
        for result in data.get("results", [])
    }
