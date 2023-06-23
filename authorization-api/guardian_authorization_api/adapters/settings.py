# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import os
from dataclasses import MISSING, fields
from typing import Optional, Type

from port_loader import AsyncAdapterSettingsProvider, Settings

from ..errors import SettingNotFoundError, SettingTypeError
from ..models.settings import SETTINGS_NAME_METADATA
from ..ports import SettingsPort


class EnvSettingsAdapter(SettingsPort, AsyncAdapterSettingsProvider):
    """
    This adapter loads all settings exclusively from environment variables.


    This adapter is a singleton and will be instantiated only once.
    This adapter interprets the '.' symbol in setting name as a double underscore, when
    converting to an environment variable and assumes capital letters only.

    """

    class Config:
        is_cached = True
        alias = "env"

    @staticmethod
    def setting_name_to_env(setting_name: str):
        return setting_name.replace(".", "__").upper()

    async def get_int(self, setting_name: str, default: Optional[int] = None) -> int:
        env_name = self.setting_name_to_env(setting_name)
        env_value = os.getenv(env_name, None)
        if env_value is None:
            if default is not None:
                return default
            raise SettingNotFoundError(
                f"No value for the requested setting {setting_name} could be found."
            )
        try:
            return int(env_value)
        except Exception as exc:
            raise SettingTypeError(
                f"The value '{env_value}' for the setting {setting_name} could not "
                f"be transformed to an integer."
            ) from exc

    async def get_str(self, setting_name: str, default: Optional[str] = None) -> str:
        env_name = self.setting_name_to_env(setting_name)
        env_value = os.getenv(env_name, None)
        if env_value is None:
            if default is not None:
                return default
            raise SettingNotFoundError(
                f"No value for the requested setting {setting_name} could be found."
            )
        return env_value

    async def get_bool(self, setting_name: str, default: Optional[bool] = None) -> bool:
        """
        Returns the requested setting as a boolean.

        This expects the value of the setting in the ENV to be either '0' for False
        or '1' for True. Any other value is deemed invalid and will cause a SettingTypeError.

        :param setting_name: The name of the setting to return
        :param default: The optional default value of the setting
        :return: The settings value
        :raises SettingFormatError: If the requested setting name is malformed.
        :raises SettingTypeError: If a value was found, but cannot be converted to a boolean
        :raises SettingNotFoundError: If no value for the specified setting can be found and no
        default value was specified
        """
        env_name = self.setting_name_to_env(setting_name)
        env_value = os.getenv(env_name, None)
        if env_value is None:
            if default is not None:
                return default
            raise SettingNotFoundError(
                f"No value for the requested setting {setting_name} could be found."
            )
        if env_value == "0":
            return False
        elif env_value == "1":
            return True
        raise SettingTypeError(
            f"The value '{env_value}' for the setting {setting_name} could not "
            f"be transformed to the desired type."
        )

    async def get_adapter_settings(self, settings_cls: Type[Settings]) -> Settings:
        setting_fields = fields(settings_cls)  # type: ignore[arg-type]
        settings_data = {}
        for field in setting_fields:
            settings_default = None if field.default is MISSING else field.default
            settings_name = field.metadata.get(SETTINGS_NAME_METADATA, "")
            settings_type = field.type
            settings_data[field.name] = await self.get_setting(
                settings_name, settings_type, settings_default
            )
        return settings_cls(**settings_data)
