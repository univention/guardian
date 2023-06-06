from collections import defaultdict
from importlib import metadata
from typing import Type, Optional, TypeVar, Any

from loguru import logger
from pydantic import BaseSettings, Field, ValidationError

from .errors import (
    AdapterInitializationError,
    SettingTypeError,
    SettingNotFoundError,
    AdapterConfigurationError,
    AdapterLoadingError,
)
from .ports import (
    SettingsPort,
    ConfiguredPort,
    PersistencePort,
    BasePort,
)

AdapterClassesDict = dict[str, dict[str, Type]]
PortType = TypeVar("PortType", bound=BasePort)

PORT_CLASSES = (SettingsPort, PersistencePort)


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


class AdapterContainer:
    """
    Singleton class to manage the creation and configuration of adapters.

    This class is the entrypoint for retrieving instantiated and configured
    adapters for ports in the application.
    """

    singleton: Optional["AdapterContainer"] = None

    @classmethod
    def instance(cls) -> "AdapterContainer":
        if cls.singleton is None:
            cls.singleton = AdapterContainer()
        return cls.singleton

    def __init__(
        self,
        adapter_selection: Optional[AdapterSelection] = None,
        adapter_classes: Optional[AdapterClassesDict] = None,
    ):
        self._adapter_classes = adapter_classes
        self._adapter_selection = adapter_selection
        self._adapter_settings: dict[str, dict[str, Any]] = dict()
        self._adapter_instances: dict[str, Any] = dict()
        logger.debug("Adapter Container instantiated")

    @property
    def adapter_selection(self) -> AdapterSelection:
        if not self._adapter_selection:
            try:
                self._adapter_selection = AdapterSelection()
            except ValidationError as exc:
                raise AdapterLoadingError(
                    "The configuration for the selection of adapters could not be loaded."
                ) from exc
        return self._adapter_selection

    @property
    def adapter_classes(self) -> AdapterClassesDict:
        if not self._adapter_classes:
            self._adapter_classes = load_adapter_classes()
        return self._adapter_classes

    def _instantiate_adapter(self, port_cls: Type[PortType]) -> PortType:
        """
        Instantiates an adapter for the given port type.

        The instantiated adapter class returned by this method is potentially
        not configured and thus unusable.
        """
        port_name = port_cls.__name__
        selection = self.adapter_selection.dict(by_alias=True).get(port_name, "")
        adapter_cls = self.adapter_classes.get(port_name, {}).get(selection, None)
        if adapter_cls is None:
            raise AdapterInitializationError(
                f"The selected adapter '{selection}' "
                f"for {port_name} could not be found."
            )
        if not issubclass(adapter_cls, port_cls):
            raise AdapterInitializationError(
                f"The class {adapter_cls} selected as the adapter for "
                f"{port_name} has the wrong type."
            )
        custom_logger = logger.bind(adapter_cls=adapter_cls, port_cls=port_cls)
        adapter = adapter_cls(custom_logger)
        custom_logger.debug("Adapter instantiated.")
        return adapter

    async def _get_adapter_settings(self, adapter_cls: Type[ConfiguredPort]):
        """
        Loads the settings for a given adapter class returns them.

        This method caches the settings on the AdapterContainer singleton.
        """
        settings_port = await self.get_adapter(SettingsPort)
        if adapter_cls.__name__ not in self._adapter_settings:
            settings = dict()
            for setting in adapter_cls.required_settings():
                try:
                    settings[setting[0]] = await settings_port.get_setting(
                        setting[0], setting[1], setting[2]
                    )
                except (SettingNotFoundError, SettingTypeError) as exc:
                    raise AdapterConfigurationError(
                        f"The adapter {adapter_cls.__name__} could not be configured. "
                        f"The required setting {setting[0]} could not be found or has the wrong type"
                    ) from exc
            self._adapter_settings[adapter_cls.__name__] = settings
            logger.bind(
                adapter_cls=adapter_cls,
                settings=settings,
            ).debug("Adapter settings loaded.")
        return self._adapter_settings[adapter_cls.__name__]

    async def _configure_adapter(self, adapter: ConfiguredPort):
        """
        This method takes an adapter instance and configures it.
        """
        settings = await self._get_adapter_settings(adapter.__class__)
        try:
            await adapter.configure(settings)
            logger.bind(adapter_cls=adapter.__class__, settings=settings).debug(
                "Adapter configured."
            )
        except Exception as exc:
            raise AdapterConfigurationError(
                f"The adapter {adapter.__class__.__name__} raised an exception when configured "
                f"with {settings}"
            ) from exc

    async def initialize_adapters(self):
        """
        This method can be called to initialize an adapter for each port.

        This function primarily exists to catch configuration errors early.
        """
        for port_cls in PORT_CLASSES:
            await self.get_adapter(port_cls)

    async def get_adapter(self, port_cls: Type[PortType]) -> PortType:
        """
        This method returns an adapter instance for the requested port type.

        Depending on the adapter class, the instance will be cached and reused (singleton)
        or created anew for each call to this method.
        """
        if port_cls.__name__ in self._adapter_instances:
            return self._adapter_instances[port_cls.__name__]
        instance = self._instantiate_adapter(port_cls)
        if isinstance(instance, ConfiguredPort):
            await self._configure_adapter(instance)
        if instance.is_cached:
            self._adapter_instances[port_cls.__name__] = instance
        return instance


def load_adapter_classes() -> AdapterClassesDict:
    """
    Loads all adapter classes for the ports via entry points.
    """
    adapter_classes: AdapterClassesDict = defaultdict(dict)
    for port_cls in PORT_CLASSES:
        entry_points = metadata.entry_points().get(
            f"guardian_authorization_api.{port_cls.__name__}", ()
        )
        for entry_point in entry_points:
            if entry_point.name in adapter_classes[port_cls.__name__]:
                raise AdapterLoadingError(
                    f"There already exists an adapters with the name "
                    f"'{entry_point.name}' for the port '{port_cls.__name__}'."
                )
            adapter_classes[port_cls.__name__][entry_point.name] = entry_point.load()
    logger.bind(adapter_classes=dict(adapter_classes)).debug("Adapter classes loaded.")
    return adapter_classes


def get_port(port_cls: Type[PortType], adapter_container=AdapterContainer.instance()):
    """
    Creates and returns a function that can be used as a dependency in FastAPI to retrieve an
    adapter for the specified port.
    """

    async def wrapper() -> PortType:
        return await adapter_container.get_adapter(port_cls)

    return wrapper
