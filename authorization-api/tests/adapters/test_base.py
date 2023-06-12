import os

import pytest
from guardian_authorization_api.adapters.base import (
    PORT_CLASSES,
    configure_registry,
    initialize_adapters,
)
from guardian_authorization_api.ports import (
    GetPermissionAPIPort,
    PersistencePort,
    PolicyPort,
    SettingsPort,
)
from port_loader.adapters import AsyncAdapterSettingsProvider
from port_loader.registries import AsyncAdapterRegistry


@pytest.fixture
def adapter_registry() -> AsyncAdapterRegistry:
    return AsyncAdapterRegistry()


def test_port_classes():
    assert PORT_CLASSES == (SettingsPort, PersistencePort, PolicyPort)


def test_configure_registry(adapter_registry, mocker):
    mocker.patch.dict(
        os.environ,
        {
            "GUARDIAN__AUTHZ__ADAPTER__SETTINGS_PORT": "my_settings",
            "GUARDIAN__AUTHZ__ADAPTER__PERSISTENCE_PORT": "my_persistence",
            "GUARDIAN__AUTHZ__ADAPTER__POLICY_PORT": "my_policy",
        },
    )
    register_port_mock = mocker.MagicMock()
    set_adapter_mock = mocker.MagicMock()
    load_ep_mock = mocker.MagicMock()
    adapter_registry.register_port = register_port_mock
    adapter_registry.set_adapter = set_adapter_mock
    adapter_registry.register_adapter = mocker.MagicMock()
    mocker.patch(
        "guardian_authorization_api.adapters.base.load_from_entry_point", load_ep_mock
    )
    configure_registry(adapter_registry)
    assert register_port_mock.call_args_list == [
        mocker.call(SettingsPort),
        mocker.call(PersistencePort),
        mocker.call(PolicyPort),
        mocker.call(GetPermissionAPIPort),
    ]
    assert set_adapter_mock.call_args_list == [
        mocker.call(SettingsPort, "my_settings"),
        mocker.call(PersistencePort, "my_persistence"),
        mocker.call(PolicyPort, "my_policy"),
        mocker.call(AsyncAdapterSettingsProvider, "my_settings"),
    ]
    assert load_ep_mock.call_args_list == [
        mocker.call(
            adapter_registry,
            SettingsPort,
            f"guardian_authorization_api.{SettingsPort.__name__}",
        ),
        mocker.call(
            adapter_registry,
            PersistencePort,
            f"guardian_authorization_api.{PersistencePort.__name__}",
        ),
        mocker.call(
            adapter_registry,
            PolicyPort,
            f"guardian_authorization_api.{PolicyPort.__name__}",
        ),
        mocker.call(
            adapter_registry,
            AsyncAdapterSettingsProvider,
            f"guardian_authorization_api.{SettingsPort.__name__}",
        ),
    ]


@pytest.mark.asyncio
async def test_initialize_adapters(adapter_registry, mocker):
    call_mock = mocker.AsyncMock()
    adapter_registry.get_adapter = call_mock
    await initialize_adapters(adapter_registry)
    assert call_mock.call_args_list == [
        mocker.call(SettingsPort),
        mocker.call(PersistencePort),
        mocker.call(PolicyPort),
    ]
