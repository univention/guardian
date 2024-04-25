# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import asyncio
import os
from typing import Callable, Optional
from unittest.mock import AsyncMock

import guardian_authorization_api
import pytest
import pytest_asyncio
import requests
from faker import Faker
from guardian_authorization_api.logging import configure_logger
from guardian_authorization_api.main import app
from guardian_authorization_api.models.policies import PolicyObject, Role
from opa_client import client as opa_client
from starlette.testclient import TestClient

from tests.mock_classes import UDMMock

fake = Faker()


@pytest_asyncio.fixture(autouse=True)
async def setup_logging():
    await configure_logger()


@pytest.fixture(scope="session")
def patch_env():
    _environ = os.environ.copy()
    os.environ["GUARDIAN__AUTHZ__ADAPTER__SETTINGS_PORT"] = "env"
    os.environ["GUARDIAN__AUTHZ__ADAPTER__PERSISTENCE_PORT"] = "udm_data"
    os.environ["GUARDIAN__AUTHZ__ADAPTER__POLICY_PORT"] = "opa"
    os.environ["OPA_ADAPTER__URL"] = os.environ.get(
        "OPA_ADAPTER__URL", "http://opa:8181"
    )
    os.environ["UDM_DATA_ADAPTER__URL"] = os.environ.get(
        "UDM_DATA_ADAPTER__URL", "http://localhost"
    )
    os.environ["UDM_DATA_ADAPTER__USERNAME"] = os.environ.get(
        "UDM_DATA_ADAPTER__USERNAME", "Administrator"
    )
    os.environ["UDM_DATA_ADAPTER__PASSWORD"] = os.environ.get(
        "UDM_DATA_ADAPTER__PASSWORD", "univention"
    )
    os.environ[
        "GUARDIAN__AUTHZ__ADAPTER__AUTHENTICATION_PORT"
    ] = "fast_api_always_authorized"
    os.environ["OAUTH_ADAPTER__WELL_KNOWN_URL"] = "/dev/zero"
    yield
    os.environ.clear()
    os.environ.update(_environ)


@pytest_asyncio.fixture(scope="session")
async def client(patch_env):
    with TestClient(app) as client:
        yield client


@pytest.fixture()
def opa_async_mock():
    """Mock the check_policy method of the OPA client"""
    check_policy = opa_client.OPAClient.check_policy
    opa_client.OPAClient.check_policy = AsyncMock()
    opa_client.OPAClient.check_policy.return_value = []
    yield opa_client.OPAClient.check_policy
    opa_client.OPAClient.check_policy = check_policy


@pytest.fixture
def get_policy_object() -> Callable:
    def _get_policy_object(
        identifier: str,
        roles: Optional[list[Role]] = None,
        attributes: Optional[dict] = None,
    ):
        roles = [] if roles is None else roles
        attributes = {} if attributes is None else attributes
        return PolicyObject(id=identifier, roles=roles, attributes=attributes)

    return _get_policy_object


def get_authz_permission_dict() -> dict:
    return {
        "app_name": fake.pystr(),
        "namespace_name": fake.pystr(),
        "name": fake.pystr(),
    }


def get_authz_context_dict() -> dict:
    return {
        "app_name": fake.pystr(),
        "namespace_name": fake.pystr(),
        "name": fake.pystr(),
    }


def get_authz_roles_dict() -> dict:
    return {
        "app_name": fake.pystr(),
        "namespace_name": fake.pystr(),
        "name": fake.pystr(),
    }


def get_authz_object_dict(id=None, n_roles=3, n_attributes=3) -> dict:
    return {
        "id": id if id else f"uid={fake.unique.pystr()}",
        "roles": [get_authz_roles_dict() for _ in range(n_roles)],
        "attributes": fake.pydict(n_attributes, value_types=[int, str]),
    }


def get_target_dict(id=None) -> dict:
    if id is None:
        return {
            "old_target": get_authz_object_dict(),
            "new_target": get_authz_object_dict(),
        }
    else:
        return {
            "old_target": get_authz_object_dict(id=id),
            "new_target": get_authz_object_dict(id=id),
        }


def get_namespace_dict() -> dict:
    return {"app_name": fake.pystr(), "name": fake.pystr()}


def get_authz_permissions_check_request_dict(
    n_actor_roles=3,
    n_namespaces=3,
    n_targets=3,
    n_context=3,
    n_extra_request_data=3,
    n_general_permissions=3,
    n_permissions=3,
) -> dict:
    return {
        "namespaces": [get_namespace_dict() for _ in range(n_namespaces)],
        "actor": get_authz_object_dict(n_roles=n_actor_roles),
        "targets": [get_target_dict() for _ in range(n_targets)],
        "contexts": [get_authz_context_dict() for _ in range(n_context)],
        "targeted_permissions_to_check": [
            get_authz_permission_dict() for _ in range(n_permissions)
        ],
        "general_permissions_to_check": [
            get_authz_permission_dict() for _ in range(n_general_permissions)
        ],
        "extra_request_data": fake.pydict(n_extra_request_data, value_types=[str, int]),
    }


def get_authz_permissions_get_request_dict(
    n_actor_roles=3,
    n_namespaces=3,
    n_targets=3,
    n_context=3,
    n_extra_request_data=3,
) -> dict:
    return {
        "namespaces": [get_namespace_dict() for _ in range(n_namespaces)],
        "actor": get_authz_object_dict(n_roles=n_actor_roles),
        "targets": [get_target_dict() for _ in range(n_targets)],
        "contexts": [get_authz_context_dict() for _ in range(n_context)],
        "include_general_permissions": fake.pybool(),
        "extra_request_data": fake.pydict(n_extra_request_data, value_types=[str, int]),
    }


def opa_is_running():
    opa_url = os.environ.get("OPA_ADAPTER__URL")
    if opa_url is None:
        return False
    try:
        response = requests.get(opa_url)
    except requests.exceptions.ConnectionError:
        return False
    return response.status_code == 200


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def opa_check_permissions_mock():
    old_method = (
        guardian_authorization_api.adapters.policies.OPAAdapter.check_permissions
    )
    guardian_authorization_api.adapters.policies.OPAAdapter.check_permissions = (
        AsyncMock()
    )
    yield guardian_authorization_api.adapters.policies.OPAAdapter.check_permissions
    guardian_authorization_api.adapters.policies.OPAAdapter.check_permissions = (
        old_method
    )


@pytest.fixture()
def udm_mock():
    old_cls = (
        guardian_authorization_api.adapters.persistence.UDMPersistenceAdapter.udm_client
    )

    def _func(users: dict = None, groups: dict = None):
        guardian_authorization_api.adapters.persistence.UDMPersistenceAdapter.udm_client = UDMMock(
            users=users,
            groups=groups,
        )
        return (
            guardian_authorization_api.adapters.persistence.UDMPersistenceAdapter.udm_client
        )

    yield _func

    guardian_authorization_api.adapters.persistence.UDMPersistenceAdapter.udm_client = (
        old_cls
    )
