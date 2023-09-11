# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from functools import partial

from guardian_lib.adapter_registry import initialize_adapters as lib_initialize_adapters
from guardian_lib.ports import AuthenticationPort, SettingsPort
from port_loader import (
    AsyncAdapterRegistry,
    AsyncAdapterSettingsProvider,
    load_from_entry_point,
)
from pydantic import BaseSettings, Field

from guardian_authorization_api.adapters.api import FastAPIGetPermissionsAPIAdapter
from guardian_authorization_api.ports import (
    GetPermissionsAPIPort,
    PersistencePort,
    PolicyPort,
)

PORT_CLASSES = (SettingsPort, PersistencePort, PolicyPort, AuthenticationPort)


class AdapterSelection(BaseSettings):
    """
    Settings class to access the adapter selection.
    """

    settings_port: str = Field(
        ..., alias="SettingsPort", env="GUARDIAN__AUTHZ__ADAPTER__SETTINGS_PORT"
    )
    persistence_port: str = Field(
        ...,
        alias="PersistencePort",
        env="GUARDIAN__AUTHZ__ADAPTER__PERSISTENCE_PORT",
    )
    policy_port: str = Field(
        ...,
        alias="PolicyPort",
        env="GUARDIAN__AUTHZ__ADAPTER__POLICY_PORT",
    )
    authentication_port: str = Field(
        ...,
        alias="AuthenticationPort",
        env="GUARDIAN__AUTHZ__ADAPTER__AUTHENTICATION_PORT",
    )


def configure_registry(adapter_registry: AsyncAdapterRegistry):
    selection = AdapterSelection().dict(by_alias=True)
    for port_cls in PORT_CLASSES:
        adapter_registry.register_port(port_cls)
        load_from_entry_point(
            adapter_registry,
            port_cls,
            f"guardian_authorization_api.{port_cls.__name__}",
        )
        adapter_registry.set_adapter(port_cls, selection[port_cls.__name__])
    load_from_entry_point(
        adapter_registry,
        AsyncAdapterSettingsProvider,
        f"guardian_authorization_api.{SettingsPort.__name__}",
    )
    adapter_registry.set_adapter(
        AsyncAdapterSettingsProvider, selection[SettingsPort.__name__]
    )
    adapter_registry.register_port(GetPermissionsAPIPort)
    adapter_registry.register_adapter(
        GetPermissionsAPIPort, adapter_cls=FastAPIGetPermissionsAPIAdapter
    )
    adapter_registry.set_adapter(GetPermissionsAPIPort, FastAPIGetPermissionsAPIAdapter)


initialize_adapters = partial(lib_initialize_adapters, port_classes=PORT_CLASSES)
