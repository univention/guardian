# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import os

import pytest
from guardian_authorization_api.adapter_registry import (
    AdapterSelection,
    configure_registry,
)
from guardian_authorization_api.adapters.api import FastAPIGetPermissionsAPIAdapter
from guardian_authorization_api.ports import (
    GetPermissionsAPIPort,
    PersistencePort,
    PolicyPort,
)
from guardian_lib.ports import SettingsPort
from port_loader import AsyncAdapterSettingsProvider


@pytest.fixture
def adapter_selection_env():
    return {
        "GUARDIAN__AUTHZ__ADAPTER__SETTINGS_PORT": "SETTINGS_PORT",
        "GUARDIAN__AUTHZ__ADAPTER__PERSISTENCE_PORT": "PERSISTENCE_PORT",
        "GUARDIAN__AUTHZ__ADAPTER__POLICY_PORT": "POLICY_PORT",
    }


@pytest.fixture
def apply_adapter_selection_env(mocker, adapter_selection_env):
    mocker.patch.dict(os.environ, adapter_selection_env)


def test_adapter_selection_loading(adapter_selection_env, apply_adapter_selection_env):
    """
    This test ensures that we load the correct env vars for adapter selection.

    If this test fails, please check that the env var change is intended and properly
    documented!
    """
    expected_env = {
        "GUARDIAN__AUTHZ__ADAPTER__SETTINGS_PORT": "SETTINGS_PORT",
        "GUARDIAN__AUTHZ__ADAPTER__PERSISTENCE_PORT": "PERSISTENCE_PORT",
        "GUARDIAN__AUTHZ__ADAPTER__POLICY_PORT": "POLICY_PORT",
    }
    assert adapter_selection_env == expected_env
    adapter_selection = AdapterSelection()
    assert adapter_selection.policy_port == "POLICY_PORT"
    assert adapter_selection.settings_port == "SETTINGS_PORT"
    assert adapter_selection.persistence_port == "PERSISTENCE_PORT"


def test_configure_registry(mocker, apply_adapter_selection_env):
    registry_mock = mocker.MagicMock()
    load_from_ep_mock = mocker.MagicMock()
    mocker.patch(
        "guardian_authorization_api.adapter_registry.load_from_entry_point",
        load_from_ep_mock,
    )
    configure_registry(registry_mock)
    assert registry_mock.set_adapter.call_args_list == [
        mocker.call(SettingsPort, "SETTINGS_PORT"),
        mocker.call(PersistencePort, "PERSISTENCE_PORT"),
        mocker.call(PolicyPort, "POLICY_PORT"),
        mocker.call(AsyncAdapterSettingsProvider, "SETTINGS_PORT"),
        mocker.call(GetPermissionsAPIPort, FastAPIGetPermissionsAPIAdapter),
    ]
    assert registry_mock.register_port.call_args_list == [
        mocker.call(SettingsPort),
        mocker.call(PersistencePort),
        mocker.call(PolicyPort),
        mocker.call(GetPermissionsAPIPort),
    ]
    assert load_from_ep_mock.call_args_list == [
        mocker.call(
            registry_mock, SettingsPort, "guardian_authorization_api.SettingsPort"
        ),
        mocker.call(
            registry_mock, PersistencePort, "guardian_authorization_api.PersistencePort"
        ),
        mocker.call(registry_mock, PolicyPort, "guardian_authorization_api.PolicyPort"),
        mocker.call(
            registry_mock,
            AsyncAdapterSettingsProvider,
            "guardian_authorization_api.SettingsPort",
        ),
    ]
