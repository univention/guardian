from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from guardian_authorization_api.models.settings import SETTINGS_NAME_METADATA

DATA_FILE_SETTING_NAME = "static_data_adapter.data_file"


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


@dataclass
class StaticDataAdapterSettings:
    data_file_path: str = field(
        metadata={SETTINGS_NAME_METADATA: DATA_FILE_SETTING_NAME}
    )
