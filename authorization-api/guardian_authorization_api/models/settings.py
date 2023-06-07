from typing import Any, NamedTuple, Optional, Type, TypeVar


SettingType = TypeVar("SettingType", bound=int | str | bool)


class RequiredSetting(NamedTuple):
    name: str
    setting_type: Type
    default: Optional[Any]
