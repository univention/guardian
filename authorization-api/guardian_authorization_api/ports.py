from abc import ABC, abstractmethod
from typing import Optional, Type, Iterable, Any

import loguru

from .errors import SettingFormatError, SettingTypeError
from .models.persistence import PersistenceObject, ObjectType
from .models.settings import RequiredSetting, SettingType


class BasePort(ABC):
    """
    Base class for all ports.
    """

    def __init__(self, logger: "loguru.Logger"):
        self._logger = logger

    @property
    def logger(self) -> "loguru.Logger":
        return self._logger.bind()

    @property
    @abstractmethod
    def is_cached(self):
        """
        Returns whether the implementing class should be cached.

        If True the adapter will be instantiated only once and reused for subsequent requests.
        If False is, the adapter will be instantiated every time the port is requested.
        """
        raise NotImplementedError


class ConfiguredPort(BasePort, ABC):
    """
    Base class for all ports that should support configuration.
    """

    @staticmethod
    @abstractmethod
    def required_settings() -> Iterable[RequiredSetting]:
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

    Setting names are always case-insensitive. The implementing adapters might impose additional
    requirements on the adapter specific details, e.g. ENV variables must consist of capital letters.

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

    async def get_setting(
        self,
        setting_name: str,
        setting_type: Type[SettingType],
        default: Optional[SettingType] = None,
    ) -> SettingType:
        """
        This function returns a settings value.

        For the standard types str, int, float and bool please use the provided
        wrapper functions, as they might implement some special handling, that differs
        from the builtin methods for casting to those types.

        :param setting_name: The name of the setting to return
        :param setting_type: The type the setting should have.
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to the specified type
                                  or the specified type is not supported
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        self.check_setting_name_format(setting_name)
        if setting_type is str:
            return await self.get_str(setting_name, default)  # type: ignore[return-value,arg-type]
        elif setting_type is bool:
            return await self.get_bool(setting_name, default)  # type: ignore[return-value,arg-type]
        elif setting_type is int:
            return await self.get_int(setting_name, default)  # type: ignore[return-value,arg-type]
        else:
            raise SettingTypeError(
                f"The requested setting type '{setting_type.__name__}' is not supported."
            )

    @abstractmethod
    async def get_int(self, setting_name: str, default: Optional[int] = None) -> int:
        """
        Returns the requested setting as an integer.

        :param setting_name: The name of the setting to return
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to an integer
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        raise NotImplementedError

    @abstractmethod
    async def get_str(self, setting_name: str, default: Optional[str] = None) -> str:
        """
        Returns the requested setting as a string.

        :param setting_name: The name of the setting to return
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to a string
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        raise NotImplementedError

    @abstractmethod
    async def get_bool(self, setting_name: str, default: Optional[bool] = None) -> bool:
        """
        Returns the requested setting as a boolean.

        :param setting_name: The name of the setting to return
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to a boolean
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        raise NotImplementedError
