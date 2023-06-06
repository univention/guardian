from dataclasses import dataclass
from enum import Enum
from typing import Any, NamedTuple, TypeVar, Type, Optional

SettingType = TypeVar("SettingType", bound=int | str | bool)


class RequiredSetting(NamedTuple):
    name: str
    setting_type: Type
    default: Optional[Any]


class ObjectType(Enum):
    """
    Describes all the object types that should be retrievable by the PersistencePort.
    """

    USER = 0
    GROUP = 1
    UNKNOWN = 2


@dataclass
class PersistenceObject:
    """
    Actor or target retrieved from data storage.
    The ``object_type`` is a hint to the PersistencePort on how to
    construct the query to the data store, such as hinting which
    table to use or how to construct the dn.
    """

    id: str
    object_type: ObjectType
    attributes: dict[str, Any]
