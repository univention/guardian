# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
import os
from typing import Optional, Type

import guardian_lib.adapter_registry as adapter_registry
import pytest
import pytest_asyncio
from guardian_authorization_api.adapters.api import FastAPIGetPermissionsAPIAdapter
from guardian_authorization_api.adapters.persistence import UDMPersistenceAdapter
from guardian_authorization_api.adapters.policies import OPAAdapter
from guardian_authorization_api.logging import configure_logger
from guardian_authorization_api.main import app
from guardian_authorization_api.ports import (
    GetPermissionsAPIPort,
    PersistencePort,
    PolicyPort,
)
from guardian_lib.adapters.settings import EnvSettingsAdapter
from guardian_lib.ports import SettingsPort
from port_loader import AsyncAdapterRegistry, AsyncAdapterSettingsProvider, Settings
from starlette.testclient import TestClient


class DummySettingsAdapter(SettingsPort):
    """Dummy settings adapter."""

    class Config:
        alias = "dummy"

    async def get_adapter_settings(self, settings_cls: Type[Settings]) -> Settings:
        return {}

    async def get_int(self, setting_name: str, default: Optional[int] = None) -> int:
        return 0

    async def get_str(self, setting_name: str, default: Optional[str] = None) -> str:
        return ""

    async def get_bool(self, setting_name: str, default: Optional[bool] = None) -> bool:
        return False


@pytest_asyncio.fixture(autouse=True)
async def setup_logging():
    await configure_logger()


@pytest.fixture
@pytest.mark.usefixtures("register_test_adapters")
def client(register_test_adapters):
    return TestClient(app)


@pytest.fixture
def patch_env(sqlite_db_name, bundle_server_base_dir):
    _environ = os.environ.copy()
    os.environ["GUARDIAN__AUTHZ__ADAPTER__POLICY_PORT"] = "opa"
    os.environ["GUARDIAN__AUTHZ__ADAPTER__PERSISTENCE_PORT"] = "udm"
    os.environ["GUARDIAN__AUTHZ__ADAPTER__SETTINGS_PORT"] = "env"
    os.environ["GUARDIAN__AUTHZ__ADAPTER__APP_API_PORT"] = "APP_API_PORT"
    yield
    os.environ.clear()
    os.environ.update(_environ)


@pytest.fixture()
def register_test_adapters(patch_env):
    """Fixture that registers the test adapters."""
    for port, adapter in [
        (SettingsPort, EnvSettingsAdapter),
        (PersistencePort, UDMPersistenceAdapter),
        (PolicyPort, OPAAdapter),
        (GetPermissionsAPIPort, FastAPIGetPermissionsAPIAdapter),
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


@pytest.fixture
def sqlite_db_name(tmpdir):
    return f"/{tmpdir / 'authz.db'}"


@pytest.fixture
def bundle_server_base_dir(tmpdir):
    return f"{tmpdir / 'bundle_server'}"
