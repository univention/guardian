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

from guardian_management_api.adapters.app import FastAPIAppAPIAdapter
from guardian_management_api.adapters.context import FastAPIContextAPIAdapter
from guardian_management_api.adapters.namespace import FastAPINamespaceAPIAdapter
from guardian_management_api.adapters.permission import FastAPIPermissionAPIAdapter
from guardian_management_api.adapters.role import FastAPIRoleAPIAdapter
from guardian_management_api.ports.app import (
    AppAPIPort,
    AppPersistencePort,
)

from .adapters.authz import AlwaysAuthorizedAdapter
from .adapters.bundle_server import BundleServerAdapter
from .adapters.capability import FastAPICapabilityAPIAdapter
from .adapters.condition import FastAPIConditionAPIAdapter
from .ports.authz import ResourceAuthorizationPort
from .ports.bundle_server import BundleServerPort
from .ports.capability import CapabilityAPIPort, CapabilityPersistencePort
from .ports.condition import ConditionAPIPort, ConditionPersistencePort
from .ports.context import ContextAPIPort, ContextPersistencePort
from .ports.namespace import NamespaceAPIPort, NamespacePersistencePort
from .ports.permission import PermissionAPIPort, PermissionPersistencePort
from .ports.role import (
    RoleAPIPort,
    RolePersistencePort,
)

PORT_CLASSES = (
    SettingsPort,
    AppPersistencePort,
    ConditionPersistencePort,
    ContextPersistencePort,
    NamespacePersistencePort,
    PermissionPersistencePort,
    RolePersistencePort,
    CapabilityPersistencePort,
    AuthenticationPort,
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
    condition_persistence_port: str = Field(
        ...,
        alias="ConditionPersistencePort",
        env="GUARDIAN__MANAGEMENT__ADAPTER__CONDITION_PERSISTENCE_PORT",
    )
    context_persistence_port: str = Field(
        ...,
        alias="ContextPersistencePort",
        env="GUARDIAN__MANAGEMENT__ADAPTER__CONTEXT_PERSISTENCE_PORT",
    )
    namespace_persistence_port: str = Field(
        ...,
        alias="NamespacePersistencePort",
        env="GUARDIAN__MANAGEMENT__ADAPTER__NAMESPACE_PERSISTENCE_PORT",
    )
    permission_persistence_port: str = Field(
        ...,
        alias="PermissionPersistencePort",
        env="GUARDIAN__MANAGEMENT__ADAPTER__PERMISSION_PERSISTENCE_PORT",
    )
    role_persistence_port: str = Field(
        ...,
        alias="RolePersistencePort",
        env="GUARDIAN__MANAGEMENT__ADAPTER__ROLE_PERSISTENCE_PORT",
    )
    capability_persistence_port: str = Field(
        ...,
        alias="CapabilityPersistencePort",
        env="GUARDIAN__MANAGEMENT__ADAPTER__CAPABILITY_PERSISTENCE_PORT",
    )
    authentication_port: str = Field(
        ...,
        alias="AuthenticationPort",
        env="GUARDIAN__MANAGEMENT__ADAPTER__AUTHENTICATION_PORT",
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
    for port, adapter in [
        (AppAPIPort, FastAPIAppAPIAdapter),
        (PermissionAPIPort, FastAPIPermissionAPIAdapter),
        (ConditionAPIPort, FastAPIConditionAPIAdapter),
        (CapabilityAPIPort, FastAPICapabilityAPIAdapter),
        (BundleServerPort, BundleServerAdapter),
        (RoleAPIPort, FastAPIRoleAPIAdapter),
        (ContextAPIPort, FastAPIContextAPIAdapter),
        (NamespaceAPIPort, FastAPINamespaceAPIAdapter),
        (ResourceAuthorizationPort, AlwaysAuthorizedAdapter),
    ]:
        adapter_registry.register_port(port)
        adapter_registry.register_adapter(port, adapter_cls=adapter)
        adapter_registry.set_adapter(port, adapter)


initialize_adapters = partial(lib_initialize_adapters, port_classes=PORT_CLASSES)
