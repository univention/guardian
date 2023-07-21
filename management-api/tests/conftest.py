import os
from typing import Optional

import guardian_management_api.adapter_registry as adapter_registry
import pytest
from guardian_management_api.adapters.app import (
    AppStaticDataAdapter,
    FastAPIAppAPIAdapter,
)
from guardian_management_api.ports.app import (
    AppAPIPort,
    AppPersistencePort,
)
from guardian_management_api.ports.settings import SettingsPort
from port_loader import AsyncAdapterRegistry


class DummySettingsAdapter(SettingsPort):
    """Dummy settings adapter."""

    class Config:
        alias = "dummy"

    async def get_int(self, setting_name: str, default: Optional[int] = None) -> int:
        return 0

    async def get_str(self, setting_name: str, default: Optional[str] = None) -> str:
        return ""

    async def get_bool(self, setting_name: str, default: Optional[bool] = None) -> bool:
        return False


@pytest.fixture()
def register_test_adapters():
    """Fixture that registers the test adapters.

    In this case:
      - In-memory app persistence adapter.
      - Dummy settings adapter.
    """
    _environ = os.environ.copy()
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__APP_PERSISTENCE_PORT"] = "in_memory"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__SETTINGS_PORT"] = "dummy"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__APP_API_PORT"] = "APP_API_PORT"
    adapter_registry.ADAPTER_REGISTRY.register_port(SettingsPort)
    adapter_registry.ADAPTER_REGISTRY.register_adapter(
        SettingsPort,
        adapter_cls=DummySettingsAdapter,
    )
    adapter_registry.ADAPTER_REGISTRY.set_adapter(
        SettingsPort,
        DummySettingsAdapter,
    )
    adapter_registry.ADAPTER_REGISTRY.register_port(AppPersistencePort)
    adapter_registry.ADAPTER_REGISTRY.register_adapter(
        AppPersistencePort,
        adapter_cls=AppStaticDataAdapter,
    )
    adapter_registry.ADAPTER_REGISTRY.set_adapter(
        AppPersistencePort,
        AppStaticDataAdapter,
    )
    adapter_registry.ADAPTER_REGISTRY.register_port(AppAPIPort)
    adapter_registry.ADAPTER_REGISTRY.register_adapter(
        AppAPIPort,
        adapter_cls=FastAPIAppAPIAdapter,
    )
    adapter_registry.ADAPTER_REGISTRY.set_adapter(
        AppAPIPort,
        FastAPIAppAPIAdapter,
    )

    yield adapter_registry.ADAPTER_REGISTRY
    os.environ.clear()
    os.environ.update(_environ)
    adapter_registry.ADAPTER_REGISTRY = AsyncAdapterRegistry()
