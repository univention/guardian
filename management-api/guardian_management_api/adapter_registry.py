# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from functools import partial

from guardian_lib.adapter_registry import initialize_adapters as lib_initialize_adapters
from guardian_lib.ports import SettingsPort
from port_loader import (
    AsyncAdapterRegistry,
    AsyncAdapterSettingsProvider,
    load_from_entry_point,
)
from pydantic import BaseSettings, Field

from guardian_management_api.adapters.app import FastAPIAppAPIAdapter
from guardian_management_api.ports.app import (
    AppAPIPort,
    AppPersistencePort,
)

from .ports.condition import ConditionPersistencePort
from .ports.context import ContextPersistencePort
from .ports.namespace import NamespacePersistencePort
from .ports.permission import PermissionPersistencePort
from .ports.role import RolePersistencePort

PORT_CLASSES = (
    SettingsPort,
    AppPersistencePort,
    ConditionPersistencePort,
    ContextPersistencePort,
    NamespacePersistencePort,
    PermissionPersistencePort,
    RolePersistencePort,
)


class AdapterSelection(BaseSettings):
    """
    Settings class to access the adapter selection.
    """

    settings_port: str = Field(
        ..., alias="SettingsPort", env="GUARDIAN__MANAGEMENT__ADAPTER__SETTINGS_PORT"
    )
    app_persistence_port: str = Field(
        ...,
        alias="AppPersistencePort",
        env="GUARDIAN__MANAGEMENT__ADAPTER__APP_PERSISTENCE_PORT",
    )


def configure_registry(adapter_registry: AsyncAdapterRegistry):
    selection = AdapterSelection().dict(by_alias=True)
    for port_cls in PORT_CLASSES:
        adapter_registry.register_port(port_cls)
        load_from_entry_point(
            adapter_registry,
            port_cls,
            f"guardian_management_api.{port_cls.__name__}",
        )
        adapter_registry.set_adapter(port_cls, selection[port_cls.__name__])
    load_from_entry_point(
        adapter_registry,
        AsyncAdapterSettingsProvider,
        f"guardian_management_api.{SettingsPort.__name__}",
    )
    adapter_registry.set_adapter(
        AsyncAdapterSettingsProvider, selection[SettingsPort.__name__]
    )
    adapter_registry.register_port(AppAPIPort)
    adapter_registry.register_adapter(AppAPIPort, adapter_cls=FastAPIAppAPIAdapter)
    adapter_registry.set_adapter(AppAPIPort, FastAPIAppAPIAdapter)


initialize_adapters = partial(lib_initialize_adapters, port_classes=PORT_CLASSES)
