# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import os
from typing import Callable, Optional
from unittest.mock import AsyncMock

import guardian_lib.adapter_registry as adapter_registry
import pytest
import pytest_asyncio
from faker import Faker
from guardian_authorization_api.adapters.api import (
    FastAPICheckPermissionsAPIAdapter,
    FastAPIGetPermissionsAPIAdapter,
)
from guardian_authorization_api.adapters.persistence import UDMPersistenceAdapter
from guardian_authorization_api.adapters.policies import OPAAdapter
from guardian_authorization_api.logging import configure_logger
from guardian_authorization_api.main import app
from guardian_authorization_api.models.policies import PolicyObject
from guardian_authorization_api.ports import (
    CheckPermissionsAPIPort,
    GetPermissionsAPIPort,
    PersistencePort,
    PolicyPort,
)
from guardian_lib.adapters.settings import EnvSettingsAdapter
from guardian_lib.ports import SettingsPort
from opa_client import client as opa_client
from port_loader import AsyncAdapterRegistry, AsyncAdapterSettingsProvider
from starlette.testclient import TestClient

fake = Faker()


@pytest_asyncio.fixture(autouse=True)
async def setup_logging():
    await configure_logger()


@pytest.fixture
def patch_env():
    _environ = os.environ.copy()
    os.environ["GUARDIAN__AUTHZ__ADAPTER__SETTINGS_PORT"] = "env"
    os.environ["GUARDIAN__AUTHZ__ADAPTER__PERSISTENCE_PORT"] = "udm_data"
    os.environ["GUARDIAN__AUTHZ__ADAPTER__POLICY_PORT"] = "opa"
    os.environ["OPA_ADAPTER__URL"] = "http://opa:8181"
    yield
    os.environ.clear()
    os.environ.update(_environ)


@pytest.fixture()
@pytest.mark.usefixtures("register_test_adapters")
def client(register_test_adapters):
    return TestClient(app)


@pytest.fixture()
def register_test_adapters(patch_env):
    """Fixture that registers the test adapters.

    In this case:
      - In-memory app persistence adapter.
      - Dummy settings adapter.
    """
    for port, adapter in [
        (SettingsPort, EnvSettingsAdapter),
        (CheckPermissionsAPIPort, FastAPICheckPermissionsAPIAdapter),
        (GetPermissionsAPIPort, FastAPIGetPermissionsAPIAdapter),
        (PolicyPort, OPAAdapter),
        (PersistencePort, UDMPersistenceAdapter),
    ]:
        adapter_registry.ADAPTER_REGISTRY.register_port(port)
        adapter_registry.ADAPTER_REGISTRY.register_adapter(port, adapter_cls=adapter)
        adapter_registry.ADAPTER_REGISTRY.set_adapter(port, adapter)
    adapter_registry.ADAPTER_REGISTRY.register_adapter(
        AsyncAdapterSettingsProvider, adapter_cls=EnvSettingsAdapter
    )
    adapter_registry.ADAPTER_REGISTRY.set_adapter(
        AsyncAdapterSettingsProvider, EnvSettingsAdapter
    )

    yield adapter_registry.ADAPTER_REGISTRY
    adapter_registry.ADAPTER_REGISTRY = AsyncAdapterRegistry()


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
        roles: Optional[list[str]] = None,
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
        "id": id if id else fake.unique.pystr(),
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
        "permissions_to_check": [
            get_authz_permission_dict() for _ in range(n_permissions)
        ],
        "general_permissions_to_check": [
            get_authz_permission_dict() for _ in range(n_general_permissions)
        ],
        "extra_request_data": fake.pydict(n_extra_request_data, value_types=[str, int]),
    }


@pytest.fixture()
def get_authz_permissions_get_request_dict(
    get_target_dict,
    get_authz_object_dict,
    get_namespace_dict,
    get_authz_context_dict,
    get_authz_permission_dict,
) -> Callable:
    def _get_authz_permissions_get_request_dict(
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
            "extra_request_data": fake.pydict(
                n_extra_request_data, value_types=[str, int]
            ),
        }

    return _get_authz_permissions_get_request_dict
