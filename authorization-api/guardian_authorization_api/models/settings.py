from typing import TypeVar

SettingType = TypeVar("SettingType", bound=int | str | bool)
SETTINGS_NAME_METADATA = "guardian_authz_settings_name"
