from abc import ABC, abstractmethod
from typing import Generic, Type

from port_loader.models import Settings


class AsyncAdapterSettingsProvider(ABC):
    """
    Abstract base class for the AsyncAdapterSettingsProvider port.

    If you use any async configured adapters you need to register at least one
    adapter for this port to provide the settings your configured adapters need.
    """

    @abstractmethod
    async def get_adapter_settings(self, settings_cls: Type[Settings]) -> Settings:
        """
        This method gets a data class type and is expected to return an instance of that dataclass.
        """
        raise NotImplementedError  # pragma: no cover


class AsyncConfiguredAdapterMixin(ABC, Generic[Settings]):
    """
    Mixin for async configured adapters.

    If you create adapters that need any form of configuration or settings
    you need to inherit from this class. This way the registry knows that it has to
    fetch settings for it.
    """

    @classmethod
    @abstractmethod
    def get_settings_cls(cls) -> Type[Settings]:
        """
        Returns the data class type which is expected as the parameter in the configure method.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def configure(self, settings: Settings):
        """
        This method is called by the registry after instantiation.

        You can rely on every field of the settings object to be set.

        :param settings: An instance of the data class type specified in the
        get_settings_cls method.
        """
        raise NotImplementedError  # pragma: no cover
