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
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from guardian_management_api.adapters.app import FastAPIAppAPIAdapter
from guardian_management_api.adapters.context import FastAPIContextAPIAdapter
from guardian_management_api.adapters.namespace import FastAPINamespaceAPIAdapter
from guardian_management_api.adapters.permission import FastAPIPermissionAPIAdapter
from guardian_management_api.adapters.role import FastAPIRoleAPIAdapter
from guardian_management_api.ports.app import (
    AppAPIPort,
    AppPersistencePort,
)

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
    ResourceAuthorizationPort,
)


class AdapterSelection(BaseSettings):
    """
    Settings class to access the adapter selection.
    """

    model_config = SettingsConfigDict(
        env_prefix="GUARDIAN__MANAGEMENT__ADAPTER__",
        populate_by_name=True,
    )

    settings_port: str = Field(..., alias="SettingsPort")
    app_persistence_port: str = Field(..., alias="AppPersistencePort")
    condition_persistence_port: str = Field(..., alias="ConditionPersistencePort")
    context_persistence_port: str = Field(..., alias="ContextPersistencePort")
    namespace_persistence_port: str = Field(..., alias="NamespacePersistencePort")
    permission_persistence_port: str = Field(..., alias="PermissionPersistencePort")
    role_persistence_port: str = Field(..., alias="RolePersistencePort")
    capability_persistence_port: str = Field(..., alias="CapabilityPersistencePort")
    authentication_port: str = Field(..., alias="AuthenticationPort")
    resource_authorization_port: str = Field(..., alias="ResourceAuthorizationPort")


def configure_registry(adapter_registry: AsyncAdapterRegistry):
    selection = AdapterSelection().model_dump(by_alias=True)
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
    ]:
        adapter_registry.register_port(port)
        adapter_registry.register_adapter(port, adapter_cls=adapter)
        adapter_registry.set_adapter(port, adapter)


initialize_adapters = partial(lib_initialize_adapters, port_classes=PORT_CLASSES)
