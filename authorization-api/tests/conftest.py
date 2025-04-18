# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

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
from guardian_authorization_api.udm_client import UDM
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
    os.environ["GUARDIAN__AUTHZ__ADAPTER__AUTHENTICATION_PORT"] = (
        "fast_api_always_authorized"
    )
    os.environ["OAUTH_ADAPTER__WELL_KNOWN_URL"] = "/dev/zero"
    yield
    os.environ.clear()
    os.environ.update(_environ)


@pytest.fixture
def ldap_base():
    return os.environ["LDAP_BASE"]


@pytest_asyncio.fixture(scope="session")
async def client(patch_env):
    with TestClient(app) as client:
        yield client


@pytest.fixture()
def create_test_user_with_udm(patch_env):
    """Create a test user within UDM"""

    udm_client = UDM(
        os.environ["UDM_DATA_ADAPTER__URL"],
        os.environ["UDM_DATA_ADAPTER__USERNAME"],
        os.environ["UDM_DATA_ADAPTER__PASSWORD"],
    )

    users_module = udm_client.get("users/user")

    users = []

    def _create_user_with_udm(
        guardian_roles: Optional[list[str]] = None, groups: Optional[list[str]] = None
    ):
        user_obj = users_module.new()
        user_obj.properties["username"] = fake.unique.pystr(max_chars=15, prefix="test")
        user_obj.properties["password"] = "univention"
        user_obj.properties["lastname"] = fake.unique.pystr(max_chars=15, prefix="test")

        if guardian_roles is not None:
            user_obj.properties["guardianRoles"] = guardian_roles

        if groups is not None:
            user_obj.properties["groups"] = groups

        user_obj.save(reload=False)
        user_obj = users_module.get(
            user_obj.dn, properties=["guardianInheritedRoles", "*"]
        )
        users.append(user_obj.dn)
        return user_obj

    yield _create_user_with_udm

    for user_dn in users:
        user = users_module.get(user_dn)
        user.delete()


@pytest.fixture()
def create_test_group_with_udm(patch_env):
    udm_client = UDM(
        os.environ["UDM_DATA_ADAPTER__URL"],
        os.environ["UDM_DATA_ADAPTER__USERNAME"],
        os.environ["UDM_DATA_ADAPTER__PASSWORD"],
    )

    groups_module = udm_client.get("groups/group")

    groups = []

    def _create_group_with_udm(guardian_member_roles: Optional[list[str]] = None):
        group_obj = groups_module.new()
        group_obj.properties["name"] = fake.unique.pystr(max_chars=15, prefix="test")

        if guardian_member_roles is not None:
            group_obj.properties["guardianMemberRoles"] = guardian_member_roles

        group_obj.save()
        groups.append(group_obj.dn)
        return group_obj

    yield _create_group_with_udm

    for group_dn in groups:
        group = groups_module.get(group_dn)
        group.delete()


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
