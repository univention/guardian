# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from abc import ABC, abstractmethod
from typing import Optional, Type

import loguru
from port_loader import AsyncAdapterSettingsProvider

from .errors import SettingFormatError, SettingTypeError
from .models.settings import SettingType


class BasePort(ABC):
    """
    Base class for all ports.
    """

    @property
    def logger(self) -> "loguru.Logger":
        return loguru.logger.bind()


class SettingsPort(BasePort, AsyncAdapterSettingsProvider, ABC):
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
        raise NotImplementedError  # pragma: no cover

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
        raise NotImplementedError  # pragma: no cover

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
        raise NotImplementedError  # pragma: no cover


class AuthenticationPort(BasePort):
    pass


class ActorIdentifierPort(BasePort):
    pass
