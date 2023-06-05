from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Type, Iterable, Tuple, Any, Callable

import loguru

from .errors import SettingFormatError
from .models.ports import PersistenceObject, ObjectType

SettingType = TypeVar("SettingType")


class BasePort(ABC):
    """
    Base class for all ports.
    """

    def __init__(self, logger: "loguru.Logger"):
        self.logger = logger

    @property
    @abstractmethod
    def is_singleton(self):
        """
        Returns True if the implementing class should be treated as a Singleton.

        If False is returned, the adapter will be instantiated every time the port is requested.
        """
        raise NotImplementedError


class ConfiguredPort(BasePort, ABC):
    """
    Base class for all ports that should support configuration.
    """

    @staticmethod
    @abstractmethod
    def required_settings() -> Iterable[Tuple[str, Type, Any]]:
        """
        Returns a list of settings that the adapter requires to configure itself.

        The format of the returned settings are tuples containing
        (setting name, setting type, default value) just as the SettingsPort expects
        for fetching settings.

        :return: A list containing the required settings for the configure method
        """
        raise NotImplementedError

    @abstractmethod
    async def configure(self, settings: dict[str, Any]):
        """
        Method to configure the adapter.

        This method is called after instantiation, but before the adapter is ever used.

        :param settings: The settings fetched from the SettingsPort
        """
        raise NotImplementedError


class PersistencePort(ConfiguredPort, ABC):
    """
    This port enables access to objects in a persistent database.

    It is used to fetch actors and targets when the API is only provided with identifiers
    and not the full objects.
    """

    @abstractmethod
    async def get_object(
        self, identifier: str, object_type: ObjectType
    ) -> PersistenceObject:
        """
        Fetches an object from the persistent database and returns it.

        :param identifier: The identifier for the object to retrieve
        :param object_type: The type of the object to retrieve
        :return: The object
        :raises ObjectNotFoundError: If the requested object could not be found
        :raises PersistenceError: For any errors other than object not found
        """
        raise NotImplementedError


class SettingsPort(BasePort, ABC):
    """
    This port enables access to settings defined for the application.

    All adapters and application settings will be retrieved through this port. The only exception
    are the configuration of which adapters to initialize and potential settings the SettingsPort
    adapter itself might need.

    Any setting name is an alphanumeric sequence of characters, where '.', '_' and '-' are
    also allowed. The '.' character has special meaning and might be used by adapters to model
    object hierarchies or similar.

    Notes for implementing adapters:
        - The code to fetch the settings should ideally be lazy loaded, if access to resources
          is required
        - The code to fetch settings should ideally be cached
    """

    @staticmethod
    def check_setting_name_format(setting_name: str):
        """
        Checks if setting_name is a valid setting name.

        Only [a-zA-Z0-9.-_] is allowed.

        :param setting_name: The setting name to check
        :raises SettingFormatError: If the setting name does not follow the defined format
        """
        check_str = setting_name.replace("-", "").replace("_", "").replace(".", "")
        if not check_str.isalnum():
            raise SettingFormatError(
                f"The requested setting '{setting_name}' does not follow the setting name format "
                f"and thus cannot be processed."
            )

    @abstractmethod
    async def get_setting(
        self,
        setting_name: str,
        setting_type: Callable[[Any], SettingType],
        default: Optional[SettingType] = None,
    ) -> SettingType:
        """
        This function returns a settings value.

        For the standard types str, int, float and bool please use the provided
        wrapper functions, as they might implement some special handling, that differs
        from the builtin methods for casting to those types.

        :param setting_name: The name of the setting to return
        :param setting_type: A callable returning a value in the desired data type when given the
                             raw setting value
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to the specified type
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        raise NotImplementedError

    async def get_int(self, setting_name: str, default: Optional[int] = None) -> int:
        """
        Wrapper for get_setting, where the requested type is int.

        :param setting_name: The name of the setting to return
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to the specified type
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        return await self.get_setting(setting_name, int, default)

    async def get_float(
        self, setting_name: str, default: Optional[float] = None
    ) -> float:
        """
        Wrapper for get_setting, where the requested type is float.

        :param setting_name: The name of the setting to return
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to the specified type
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        return await self.get_setting(setting_name, float, default)

    async def get_str(self, setting_name: str, default: Optional[str] = None) -> str:
        """
        Wrapper for get_setting, where the requested type is str.

        :param setting_name: The name of the setting to return
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to the specified type
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        return await self.get_setting(setting_name, str, default)

    async def get_bool(self, setting_name: str, default: Optional[bool] = None) -> bool:
        """
        Wrapper for get_setting, where the requested type is bool.

        :param setting_name: The name of the setting to return
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to the specified type
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        return await self.get_setting(setting_name, bool, default)
