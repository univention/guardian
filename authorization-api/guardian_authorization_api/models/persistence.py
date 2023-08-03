# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from guardian_authorization_api.models.settings import SETTINGS_NAME_METADATA

# Used with StaticDataAdapter
STATIC_DATA_FILE_SETTING_NAME = "static_data_adapter.data_file"

# Used with UDMPersistenceAdapter
UDM_URL_SETTINGS_NAME = "udm_data_adapter.url"
UDM_USERNAME_SETTINGS_NAME = "udm_data_adapter.username"
UDM_PASSWORD_SETTINGS_NAME = "udm_data_adapter.password"  # nosec B105


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
    roles: list[str]


@dataclass
class StaticDataAdapterSettings:
    data_file_path: str = field(
        metadata={SETTINGS_NAME_METADATA: STATIC_DATA_FILE_SETTING_NAME}
    )


@dataclass(frozen=True)
class UDMPersistenceAdapterSettings:
    url: str = field(metadata={SETTINGS_NAME_METADATA: UDM_URL_SETTINGS_NAME})
    username: str = field(metadata={SETTINGS_NAME_METADATA: UDM_USERNAME_SETTINGS_NAME})
    password: str = field(metadata={SETTINGS_NAME_METADATA: UDM_PASSWORD_SETTINGS_NAME})
