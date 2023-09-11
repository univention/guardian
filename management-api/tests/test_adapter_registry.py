# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from guardian_lib.ports import SettingsPort
from guardian_management_api.adapter_registry import (
    AdapterSelection,
    configure_registry,
)
from guardian_management_api.adapters.app import FastAPIAppAPIAdapter
from guardian_management_api.adapters.bundle_server import BundleServerAdapter
from guardian_management_api.adapters.condition import FastAPIConditionAPIAdapter
from guardian_management_api.adapters.permission import FastAPIPermissionAPIAdapter
from guardian_management_api.adapters.role import FastAPIRoleAPIAdapter
from guardian_management_api.adapters.context import FastAPIContextAPIAdapter
from guardian_management_api.adapters.permission import FastAPIPermissionAPIAdapter
from guardian_management_api.ports.app import (
    AppAPIPort,
    AppPersistencePort,
)
from guardian_management_api.ports.bundle_server import BundleServerPort
from guardian_management_api.ports.condition import (
    ConditionAPIPort,
    ConditionPersistencePort,
)
from guardian_management_api.ports.context import ContextAPIPort, ContextPersistencePort
from guardian_management_api.ports.namespace import NamespacePersistencePort
from guardian_management_api.ports.permission import (
    PermissionAPIPort,
    PermissionPersistencePort,
)
from guardian_management_api.ports.role import (
    RoleAPIPort,
    RolePersistencePort,
)
from port_loader import AsyncAdapterSettingsProvider


def test_adapter_selection_loading(patch_env):
    """
    This test ensures that we load the correct env vars for adapter selection.

    If this test fails, please check that the env var change is intended and properly
    documented!
    """
    adapter_selection = AdapterSelection()
    assert adapter_selection.settings_port == "env"
    assert adapter_selection.app_persistence_port == "sql"
    assert adapter_selection.condition_persistence_port == "sql"
    assert adapter_selection.context_persistence_port == "sql"
    assert adapter_selection.namespace_persistence_port == "sql"
    assert adapter_selection.permission_persistence_port == "sql"
    assert adapter_selection.role_persistence_port == "sql"


def test_configure_registry(mocker, register_test_adapters):
    registry_mock = mocker.MagicMock()
    load_from_ep_mock = mocker.MagicMock()
    mocker.patch(
        "guardian_management_api.adapter_registry.load_from_entry_point",
        load_from_ep_mock,
    )
    configure_registry(registry_mock)
    assert registry_mock.set_adapter.call_args_list == [
        mocker.call(SettingsPort, "env"),
        mocker.call(AppPersistencePort, "sql"),
        mocker.call(ConditionPersistencePort, "sql"),
        mocker.call(ContextPersistencePort, "sql"),
        mocker.call(NamespacePersistencePort, "sql"),
        mocker.call(PermissionPersistencePort, "sql"),
        mocker.call(RolePersistencePort, "sql"),
        mocker.call(AsyncAdapterSettingsProvider, "env"),
        mocker.call(AppAPIPort, FastAPIAppAPIAdapter),
        mocker.call(PermissionAPIPort, FastAPIPermissionAPIAdapter),
        mocker.call(ConditionAPIPort, FastAPIConditionAPIAdapter),
        mocker.call(BundleServerPort, BundleServerAdapter),
        mocker.call(RoleAPIPort, FastAPIRoleAPIAdapter),
        mocker.call(ContextAPIPort, FastAPIContextAPIAdapter),
    ]
    assert registry_mock.register_port.call_args_list == [
        mocker.call(SettingsPort),
        mocker.call(AppPersistencePort),
        mocker.call(ConditionPersistencePort),
        mocker.call(ContextPersistencePort),
        mocker.call(NamespacePersistencePort),
        mocker.call(PermissionPersistencePort),
        mocker.call(RolePersistencePort),
        mocker.call(AppAPIPort),
        mocker.call(PermissionAPIPort),
        mocker.call(ConditionAPIPort),
        mocker.call(BundleServerPort),
        mocker.call(RoleAPIPort),
        mocker.call(ContextAPIPort),
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
            ConditionPersistencePort,
            "guardian_management_api.ConditionPersistencePort",
        ),
        mocker.call(
            registry_mock,
            ContextPersistencePort,
            "guardian_management_api.ContextPersistencePort",
        ),
        mocker.call(
            registry_mock,
            NamespacePersistencePort,
            "guardian_management_api.NamespacePersistencePort",
        ),
        mocker.call(
            registry_mock,
            PermissionPersistencePort,
            "guardian_management_api.PermissionPersistencePort",
        ),
        mocker.call(
            registry_mock,
            RolePersistencePort,
            "guardian_management_api.RolePersistencePort",
        ),
        mocker.call(
            registry_mock,
            AsyncAdapterSettingsProvider,
            "guardian_management_api.SettingsPort",
        ),
    ]
