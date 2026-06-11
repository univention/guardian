# SPDX-FileCopyrightText: 2026 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

"""Shared fixtures and helpers. Talks to Cerbos at 127.0.0.1:3593; never starts or stops it."""

import os
import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, TypeVar

import pytest
from cerbos.effect.v1 import effect_pb2
from cerbos.engine.v1 import engine_pb2
from cerbos.request.v1 import request_pb2
from cerbos.sdk.grpc.client import CerbosClient
from google.protobuf.struct_pb2 import ListValue, Struct, Value

CERBOS_HOST = os.environ.get("CERBOS_HOST", "127.0.0.1:3593")
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


def _to_pb_value(v: Any) -> Value:
    if isinstance(v, bool):
        return Value(bool_value=v)
    if isinstance(v, str):
        return Value(string_value=v)
    if isinstance(v, (int, float)):
        return Value(number_value=float(v))
    if isinstance(v, dict):
        return Value(
            struct_value=Struct(fields={k: _to_pb_value(vv) for k, vv in v.items()})
        )
    if isinstance(v, list):
        return Value(list_value=ListValue(values=[_to_pb_value(i) for i in v]))
    raise TypeError(f"Unsupported attr value type: {type(v)}")


def _to_attr(d: dict[str, Any] | None) -> dict[str, Value]:
    return {k: _to_pb_value(v) for k, v in (d or {}).items()}


def check_resources(
    client: CerbosClient,
    *,
    roles: Iterable[str],
    resources: list[dict[str, Any]],
    principal_id: str = "alice",
    principal_attr: dict[str, Any] | None = None,
) -> dict[str, dict[str, str]]:
    """Returns `{resource_id: {action: "EFFECT_ALLOW"|"EFFECT_DENY"}}`.

    Each resource dict: ``{"id": str, "kind": str, "actions": list[str], "attr": dict}``
    """
    principal = engine_pb2.Principal(
        id=principal_id,
        roles=list(roles),
        attr=_to_attr(principal_attr),
    )
    entries = [
        request_pb2.CheckResourcesRequest.ResourceEntry(
            resource=engine_pb2.Resource(
                id=r["id"], kind=r["kind"], attr=_to_attr(r.get("attr"))
            ),
            actions=list(r["actions"]),
        )
        for r in resources
    ]
    resp = client.check_resources(principal=principal, resources=entries)
    return {
        result.resource.id: {
            action: effect_pb2.Effect.Name(effect)
            for action, effect in result.actions.items()
        }
        for result in resp.results
    }
