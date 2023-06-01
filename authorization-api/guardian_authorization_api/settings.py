from typing import Optional

from .ports import SettingsPort, SettingType


class EnvSettings(SettingsPort):
    async def get_setting(
        self,
        setting_name: str,
        setting_type: SettingType,
        default: Optional[SettingType] = None,
    ) -> SettingType:
        raise NotImplementedError

    @property
    def is_singleton(self):
        return True
