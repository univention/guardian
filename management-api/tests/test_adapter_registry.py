# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import inspect

import pytest
from guardian_management_api.adapter_registry import (
    PORT_CLASSES,
    AdapterSelection,
    configure_registry,
    initialize_adapters,
    port_dep,
)
from guardian_management_api.adapters.app import FastAPIAppAPIAdapter
from guardian_management_api.ports.app import (
    AppAPIPort,
    AppPersistencePort,
)
from guardian_management_api.ports.settings import SettingsPort
from port_loader import AsyncAdapterRegistry, AsyncAdapterSettingsProvider


def test_adapter_selection_loading(register_test_adapters):
    """
    This test ensures that we load the correct env vars for adapter selection.

    If this test fails, please check that the env var change is intended and properly
    documented!
    """
    adapter_selection = AdapterSelection()
    assert adapter_selection.settings_port == "dummy"
    assert adapter_selection.app_persistence_port == "in_memory"


def test_configure_registry(mocker, register_test_adapters):
    registry_mock = mocker.MagicMock()
    load_from_ep_mock = mocker.MagicMock()
    mocker.patch(
        "guardian_management_api.adapter_registry.load_from_entry_point",
        load_from_ep_mock,
    )
    configure_registry(registry_mock)
    assert registry_mock.set_adapter.call_args_list == [
        mocker.call(SettingsPort, "dummy"),
        mocker.call(AppPersistencePort, "in_memory"),
        mocker.call(AsyncAdapterSettingsProvider, "dummy"),
        mocker.call(AppAPIPort, FastAPIAppAPIAdapter),
    ]
    assert registry_mock.register_port.call_args_list == [
        mocker.call(SettingsPort),
        mocker.call(AppPersistencePort),
        mocker.call(AppAPIPort),
    ]
    assert load_from_ep_mock.call_args_list == [
        mocker.call(
            registry_mock, SettingsPort, "guardian_management_api.SettingsPort"
        ),
        mocker.call(
            registry_mock,
            AppPersistencePort,
            "guardian_management_api.AppPersistencePort",
        ),
        mocker.call(
            registry_mock,
            AsyncAdapterSettingsProvider,
            "guardian_management_api.SettingsPort",
        ),
    ]


@pytest.mark.asyncio
async def test_initialize_adapters(mocker):
    registry = AsyncAdapterRegistry()
    call_mock = mocker.AsyncMock()
    registry.request_port = call_mock
    await initialize_adapters(registry)
    assert call_mock.call_args_list == [
        mocker.call(port_cls) for port_cls in PORT_CLASSES
    ]


def test_port_dep_is_callable():
    """
    This test ensures that the return value from port_dep is a callable without
    any parameters to be used as a FastAPI dependency.
    """
    dep = port_dep(AppAPIPort)
    assert inspect.isfunction(dep)
    signature = inspect.signature(dep)
    assert len(signature.parameters) == 0


@pytest.mark.asyncio
async def test_port_dep_port_only(mocker):
    registry = AsyncAdapterRegistry()
    call_mock = mocker.AsyncMock()
    registry.request_port = call_mock
    mocker.patch("guardian_management_api.adapter_registry.ADAPTER_REGISTRY", registry)
    await port_dep(AppAPIPort)()
    assert await call_mock.called_once_with(AppAPIPort)


@pytest.mark.asyncio
async def test_port_dep_with_adapter(mocker):
    registry = AsyncAdapterRegistry()
    call_mock = mocker.AsyncMock()
    registry.request_adapter = call_mock
    mocker.patch("guardian_management_api.adapter_registry.ADAPTER_REGISTRY", registry)
    await port_dep(AppAPIPort, FastAPIAppAPIAdapter)()
    assert await call_mock.called_once_with(
        AppAPIPort,
        FastAPIAppAPIAdapter,
    )
