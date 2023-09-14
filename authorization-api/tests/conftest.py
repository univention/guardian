# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import asyncio
import json
import os

import pytest
import pytest_asyncio
from guardian_authorization_api.main import app
from guardian_lib.adapters.authentication import (
    FastAPIAlwaysAuthorizedAdapter,
    FastAPINeverAuthorizedAdapter,
)
from starlette.testclient import TestClient


@pytest.fixture(scope="session")
def patch_env(static_data_name):
    _environ = os.environ.copy()
    os.environ["GUARDIAN__AUTHZ__ADAPTER__PERSISTENCE_PORT"] = "static_data"
    os.environ["STATIC_DATA_ADAPTER__DATA_FILE"] = static_data_name
    os.environ["GUARDIAN__AUTHZ__ADAPTER__POLICY_PORT"] = "opa"
    os.environ[
        "GUARDIAN__AUTHZ__ADAPTER__AUTHENTICATION_PORT"
    ] = "fast_api_always_authorized"
    os.environ["GUARDIAN__AUTHZ__ADAPTER__SETTINGS_PORT"] = "env"
    os.environ["OPA_ADAPTER__URL"] = "/dev/zero"
    os.environ["OAUTH_ADAPTER__WELL_KNOWN_URL"] = "/dev/zero"
    yield
    os.environ.clear()
    os.environ.update(_environ)


@pytest_asyncio.fixture(scope="session")
async def client(patch_env):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def error401(monkeypatch):
    monkeypatch.setattr(
        FastAPIAlwaysAuthorizedAdapter,
        "__call__",
        FastAPINeverAuthorizedAdapter.__call__,
    )
    yield


@pytest.fixture(scope="session")
def static_data_name(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("data")
    path = os.path.join(tmpdir, "data.json")
    with open(path, "w") as static_data:
        json.dump(dict(), static_data)
    yield path
