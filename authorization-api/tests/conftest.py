# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import json
import os

import pytest
import pytest_asyncio
from guardian_authorization_api.main import app
from guardian_lib.adapter_registry import ADAPTER_REGISTRY
from guardian_lib.adapters.authentication import (
    NeverAuthorizedAdapter,
)
from guardian_lib.ports import AuthenticationPort
from starlette.testclient import TestClient


@pytest.fixture
def patch_env(static_data_name):
    _environ = os.environ.copy()
    os.environ["GUARDIAN__AUTHZ__ADAPTER__PERSISTENCE_PORT"] = "static_data"
    os.environ["STATIC_DATA_ADAPTER__DATA_FILE"] = static_data_name
    os.environ["GUARDIAN__AUTHZ__ADAPTER__POLICY_PORT"] = "opa"
    os.environ["GUARDIAN__AUTHZ__ADAPTER__AUTHENTICATION_PORT"] = "always_authorized"
    os.environ["GUARDIAN__AUTHZ__ADAPTER__SETTINGS_PORT"] = "env"
    os.environ["OPA_ADAPTER__URL"] = "/dev/zero"
    yield
    os.environ.clear()
    os.environ.update(_environ)


@pytest.fixture()
def client(patch_env):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def static_data_name(tmpdir):
    path = os.path.join(tmpdir, "data.json")
    with open(path, "w") as static_data:
        json.dump(dict(), static_data)
    yield path


@pytest_asyncio.fixture(scope="function")
async def never_authorized():
    old_adapter = await ADAPTER_REGISTRY(AuthenticationPort)
    ADAPTER_REGISTRY.set_adapter(AuthenticationPort, NeverAuthorizedAdapter)
    yield
    ADAPTER_REGISTRY.set_adapter(AuthenticationPort, old_adapter.__class__)
