# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


from guardian_lib.ports import SettingsPort
from guardian_management_api.adapter_registry import (
    AdapterSelection,
    configure_registry,
)
from guardian_management_api.adapters.app import FastAPIAppAPIAdapter
from guardian_management_api.ports.app import (
    AppAPIPort,
    AppPersistencePort,
)
from port_loader import AsyncAdapterSettingsProvider


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
