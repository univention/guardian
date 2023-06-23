# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from collections import defaultdict
from dataclasses import asdict
from typing import Any, Optional, Type, cast

from loguru import logger

from .adapters import AsyncAdapterSettingsProvider, AsyncConfiguredAdapterMixin
from .errors import (
    AdapterConfigurationError,
    AdapterInstantiationError,
    AdapterNotFoundError,
    AdapterNotSetError,
    DuplicateAdapterError,
    DuplicatePortError,
    PortNotFoundError,
    PortSubclassError,
)
from .injection import inject_adapter
from .models import Adapter, AdapterConfiguration, Port, PortConfiguration
from .utils import get_fqcn


class AsyncAdapterRegistry:
    """
    This is an Async adapter registry.

    This class allows to register ports and adapters for those ports.
    It allows to request an object instance for a given port without knowing
    which specific implementation (adapter) is used.

    The adapter registry can be called directly to request a port object instance, e.g.:

    port_adapter = await adapter_registry(SomePortClass)
    """

    def __init__(self) -> None:
        self._adapter_configs: dict[str, dict[str, AdapterConfiguration]] = defaultdict(
            dict
        )
        self._port_configs: dict[str, PortConfiguration] = {}
        self._cached_adapters: dict[str, Any] = {}
        self.register_port(AsyncAdapterSettingsProvider)

    async def __call__(self, port_cls: Type, adapter_cls: Optional[Type] = None):
        if adapter_cls:
            return await self.request_adapter(port_cls, adapter_cls)
        else:
            return await self.request_port(port_cls)

    async def _configure_adapter(self, adapter: AsyncConfiguredAdapterMixin):
        local_logger = logger.bind(adaper=get_fqcn(adapter.__class__))
        settings_provider = await self.request_port(AsyncAdapterSettingsProvider)
        settings = await settings_provider.get_adapter_settings(
            adapter.get_settings_cls()
        )
        local_logger = local_logger.bind(settings=asdict(settings))
        await adapter.configure(settings)
        local_logger.info("Adapter configured.")

    def _create_adapter_config(
        self, adapter_cls: Type[Adapter]
    ) -> AdapterConfiguration:
        adapter_config_cls = getattr(adapter_cls, "Config", None)
        alias = getattr(adapter_config_cls, "alias", None)
        return AdapterConfiguration(
            adapter_cls=adapter_cls,
            is_cached=getattr(adapter_config_cls, "is_cached", True),
            alias=alias,
        )

    async def _get_or_create_adapter_instance(
        self,
        port_fqcn: str,
        adapter_fqcn: str,
        adapter_config: AdapterConfiguration,
    ) -> Adapter:
        local_logger = logger.bind(port=port_fqcn, adapter=adapter_fqcn)
        adapter_cls = adapter_config.adapter_cls
        cached_adapter = self._cached_adapters.get(adapter_fqcn)
        if cached_adapter and isinstance(cached_adapter, adapter_cls):
            local_logger.bind(adapter_cached=True).debug("Adapter retrieved.")
            return cached_adapter
        try:
            adapter = adapter_cls()
        except Exception as exc:
            raise AdapterInstantiationError(
                f"An error occurred during the instantiation of adapter '{adapter_fqcn}' "
                f"for the port '{port_fqcn}'."
            ) from exc
        if isinstance(adapter, AsyncConfiguredAdapterMixin):
            local_logger = logger.bind(adapter_configured=True)
            try:
                await self._configure_adapter(adapter)
            # This happens when the adapter uses an AsyncConfiguredAdapterMixin
            # and no adapter is set for the AsyncAdapterSettingsProvider port
            except AdapterNotSetError as exc:
                raise exc
            except Exception as exc:
                raise AdapterConfigurationError(
                    f"The adapter '{adapter_fqcn}' could not be configured."
                ) from exc
        if adapter_config.is_cached is True:
            self._cached_adapters[adapter_fqcn] = adapter
        local_logger.bind(adapter_cached=False).debug("Adapter retrieved.")
        return adapter

    def register_port(self, port_cls: Type[Port]) -> Type[Port]:
        """
        Registers a port with the adapter registry.

        :param port_cls: The port class to register
        :raises DuplicatePortError: If the port class was already registered
        """
        port_fqcn = get_fqcn(port_cls)
        local_logger = logger.bind(port=port_fqcn)
        if port_fqcn in self._port_configs:
            raise DuplicatePortError(
                f"A port with the name '{port_fqcn}' was already registered."
            )
        self._port_configs[port_fqcn] = PortConfiguration(port_cls=port_cls)
        local_logger.info("Port registered.")
        return port_cls

    def register_adapter(
        self,
        port_cls: Type,
        *,
        adapter_cls: Optional[Type[Adapter]] = None,
    ):
        """
        This method returns a class decorator that can be used to register an adapter for a given port.
        If the optional parameter adapter_cls is supplied to this function, the decorator
        is immediately applied to that adapter class.

        If the registered adapter specifies inject_port() parameters, the adapters method are augmented
        here.

        The documented exceptions are raised by the decorator function, not this method itself!

        :param port_cls: The port to register the adapter for
        :param adapter_cls: The class to apply the generated decorator to.
        :return: The class decorator
        :raises PortSubclassError: If the adapter is not a subclass of the specified port, or you try
        to register a ConfiguredAdapter to the AsyncAdapterSettingsProvider port
        :raises PortNotFoundError: If the port you want to register the adapter for was not
        registered before
        :raises DuplicateAdapterError: If an adapter of that type or name was already registered for
        the specified port.
        """

        def _register_adapter(adapter_cls: Type[Adapter]) -> Type[Adapter]:
            adapter_fqcn = get_fqcn(adapter_cls)
            port_fqcn = get_fqcn(port_cls)
            local_logger = logger.bind(port=port_fqcn, adapter=adapter_fqcn)
            if port_cls is AsyncAdapterSettingsProvider and issubclass(
                adapter_cls, AsyncConfiguredAdapterMixin
            ):
                raise PortSubclassError(
                    f"An adapter for the port '{port_fqcn}' must never be a ConfiguredAdapter."
                )
            if port_fqcn not in self._port_configs:
                raise PortNotFoundError(f"The port '{port_fqcn}' was not registered.")
            if not issubclass(adapter_cls, port_cls):
                raise PortSubclassError(
                    f"The adapter '{adapter_fqcn}' is not valid for port '{port_fqcn}'"
                )
            adapter_config = self._create_adapter_config(adapter_cls)
            if adapter_config.alias and any(
                (
                    other_config
                    for other_config in self._adapter_configs[port_fqcn].values()
                    if (other_config.alias == adapter_config.alias)
                )
            ):
                raise DuplicateAdapterError(
                    f"An adapter class with the alias '{adapter_config.alias}' "
                    f"has already been registered for the port {port_fqcn}."
                )
            if adapter_fqcn in self._adapter_configs[port_fqcn]:
                raise DuplicateAdapterError(
                    f"The adapter class '{adapter_fqcn}' has already been "
                    f"registered for the port '{port_fqcn}'."
                )
            inject_adapter(self, adapter_cls=adapter_cls)
            self._adapter_configs[port_fqcn][adapter_fqcn] = adapter_config
            local_logger.info("Adapter registered.")
            return adapter_cls

        if adapter_cls:
            return _register_adapter(adapter_cls)
        return _register_adapter

    def set_adapter(self, port_cls: Type, adapter_cls: Type | str):
        """
        Method to set which adapter to return if the specified port is requested.

        :param port_cls: The port to set the adapter for
        :param adapter_cls: The adapter type or adapter alias to set for the port
        :raises AdapterNotFoundError: If the specified adapter was not registered
        """
        port_fqcn = get_fqcn(port_cls)
        local_logger = logger.bind(port=port_fqcn)
        if port_fqcn not in self._port_configs:
            raise PortNotFoundError(f"The port '{port_fqcn}' was not registered.")
        if type(adapter_cls) is str:
            adapter_configs = list(
                [
                    adapter_config
                    for adapter_config in self._adapter_configs[port_fqcn].values()
                    if adapter_config.alias == adapter_cls
                ]
            )
            if len(adapter_configs) == 0:
                raise AdapterNotFoundError(
                    f"No adapter with the alias '{adapter_cls}' was registered "
                    f"for the port '{port_fqcn}'."
                )
            adapter_fqcn = get_fqcn(adapter_configs[0].adapter_cls)
        else:
            adapter_fqcn = get_fqcn(cast(Type, adapter_cls))
            if adapter_fqcn not in self._adapter_configs.get(port_fqcn, {}):
                raise AdapterNotFoundError(
                    f"No adapter of the type '{adapter_fqcn}' was registered "
                    f"for the port '{port_fqcn}'."
                )
        local_logger.bind(adapter=adapter_fqcn).info("Adapter set.")
        self._port_configs[port_fqcn].selected_adapter = adapter_fqcn

    async def request_port(self, port_cls: Type[Port]) -> Port:
        """
        Method to get an object instance for the requested port.

        This will be an instance of the type of the adapter class set for
        the port.

        If multiple adapters were registered for the specified port, but none was set,
        an exception is raised. If only one adapter was registered for the port though,
        it is automatically assumed that this adapter was set for the port.

        This method can be called directly by calling the registry instance as well.

        :param port_cls: The port to retrieve the object instance for
        :return: The port/adapter object instance
        :raises PortNotFoundError: If the requested port was not registered before
        :raises AdapterNotSetError: If no adapter was set for the requested port or
        if no adapter was set for the AsyncAdapterSettingsProvider port if the requested
        port is a AsyncConfiguredAdapterMixin
        :raises AdapterInstantiationError: If there was an exception during adapter instantiation
        :raises AdapterConfigurationError: If there was an exception during adapter configuration
        """
        port_fqcn = get_fqcn(port_cls)
        try:
            adapter_fqcn = self._port_configs[port_fqcn].selected_adapter
        except KeyError:
            raise PortNotFoundError(f"The port '{port_fqcn}' was not registered.")
        if adapter_fqcn is None:
            registered_adapters = list(self._adapter_configs[port_fqcn].keys())
            if len(registered_adapters) == 1:
                adapter_fqcn = registered_adapters[0]
            else:
                raise AdapterNotSetError(
                    f"There was no adapter set for the port '{port_fqcn}'."
                )
        adapter_config = self._adapter_configs[port_fqcn][adapter_fqcn]
        return await self._get_or_create_adapter_instance(
            port_fqcn,
            adapter_fqcn,
            adapter_config,
        )

    async def request_adapter(
        self, port_cls: Type[Port], adapter_cls: Type[Adapter]
    ) -> Adapter:
        """
        Method to get an instance for the requested adapter.

        This method does not respect the set adapter for any given port,
        but returns an instance of the requested adapter class directly.

        :param adapter_cls: The class of the adapter to retrieve an object instance for
        :param port_cls: The port to retrieve the object instance for
        :return: The adapter object instance
        :raises PortNotFoundError: If the requested port was not registered before
        :raises AdapterNotSetError: If no adapter was set for the requested port or
        if no adapter was set for the AsyncAdapterSettingsProvider port if the requested
        port is a AsyncConfiguredAdapterMixin
        :raises AdapterInstantiationError: If there was an exception during adapter instantiation
        :raises AdapterConfigurationError: If there was an exception during adapter configuration
        """
        port_fqcn = get_fqcn(port_cls)
        adapter_fqcn = get_fqcn(adapter_cls)
        if port_fqcn not in self._port_configs:
            raise PortNotFoundError(f"The port '{port_fqcn}' was not registered.")
        adapter_config = self._adapter_configs.get(port_fqcn, {}).get(adapter_fqcn)
        if adapter_config is None:
            raise AdapterNotFoundError(
                f"No adapter for the type '{adapter_fqcn}' was registered "
                f"for the port '{port_fqcn}'."
            )
        return await self._get_or_create_adapter_instance(
            port_fqcn,
            adapter_fqcn,
            adapter_config,
        )
