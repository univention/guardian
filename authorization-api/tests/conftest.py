# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import os

import pytest
from guardian_authorization_api.main import app
from starlette.testclient import TestClient


@pytest.fixture
def patch_env():
    _environ = os.environ.copy()
    os.environ["GUARDIAN__AUTHZ__ADAPTER__PERSISTENCE_PORT"] = "static_data"
    os.environ["GUARDIAN__AUTHZ__ADAPTER__POLICY_PORT"] = "opa"
    os.environ["GUARDIAN__AUTHZ__ADAPTER__AUTHENTICATION_PORT"] = "never_authorized"
    os.environ["GUARDIAN__AUTHZ__ADAPTER__SETTINGS_PORT"] = "env"
    yield
    os.environ.clear()
    os.environ.update(_environ)


@pytest.fixture()
def client(patch_env):
    with TestClient(app) as client:
        yield client
