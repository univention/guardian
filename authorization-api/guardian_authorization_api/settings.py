from typing import Optional, Callable, Any

from .ports import SettingsPort, SettingType


class EnvSettings(SettingsPort):
    async def get_setting(
        self,
        setting_name: str,
        setting_type: Callable[[Any], SettingType],
        default: Optional[SettingType] = None,
    ) -> SettingType:
        raise NotImplementedError

    @property
    def is_singleton(self):
        return True
