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

from guardian_authorization_api.adapters.api import (
    FastAPICheckPermissionsAPIAdapter,
    FastAPIGetPermissionsAPIAdapter,
)
from guardian_authorization_api.ports import (
    CheckPermissionsAPIPort,
    GetPermissionsAPIPort,
    PersistencePort,
    PolicyPort,
)

PORT_CLASSES = (SettingsPort, PersistencePort, PolicyPort, AuthenticationPort)


class AdapterSelection(BaseSettings):
    """
    Settings class to access the adapter selection.
    """

    model_config = SettingsConfigDict(
        env_prefix="GUARDIAN__AUTHZ__ADAPTER__",
        populate_by_name=True,
    )

    settings_port: str = Field(..., alias="SettingsPort")
    persistence_port: str = Field(..., alias="PersistencePort")
    policy_port: str = Field(..., alias="PolicyPort")
    authentication_port: str = Field(..., alias="AuthenticationPort")


def configure_registry(adapter_registry: AsyncAdapterRegistry):
    selection = AdapterSelection().model_dump(by_alias=True)
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

    for port, adapter in [
        (GetPermissionsAPIPort, FastAPIGetPermissionsAPIAdapter),
        (CheckPermissionsAPIPort, FastAPICheckPermissionsAPIAdapter),
    ]:
        adapter_registry.register_port(port)
        adapter_registry.register_adapter(port, adapter_cls=adapter)
        adapter_registry.set_adapter(port, adapter)


initialize_adapters = partial(lib_initialize_adapters, port_classes=PORT_CLASSES)
