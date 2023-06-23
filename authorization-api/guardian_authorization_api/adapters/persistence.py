# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import json
from typing import Type

from port_loader import AsyncConfiguredAdapterMixin

from ..errors import ObjectNotFoundError, PersistenceError
from ..models.persistence import (
    ObjectType,
    PersistenceObject,
    StaticDataAdapterSettings,
)
from ..ports import PersistencePort


class StaticDataAdapter(PersistencePort, AsyncConfiguredAdapterMixin):
    """
    This adapter for the PersistencePort implements a data store that is held in memory and
    seeded by a json file that is loaded from the path configured by 'static_data_adapter.data_file'.

    This adapter is not meant for production but rather for testing purposes.
    """

    class Config:
        is_cached = True
        alias = "static_data"

    @classmethod
    def get_settings_cls(cls) -> Type[StaticDataAdapterSettings]:
        return StaticDataAdapterSettings

    async def configure(self, settings: StaticDataAdapterSettings):
        self._load_static_data(settings.data_file_path)

    def __init__(self):
        self._users = dict()
        self._groups = dict()

    async def get_object(
        self, identifier: str, object_type: ObjectType
    ) -> PersistenceObject:
        if object_type == ObjectType.USER:
            raw_object = self._users.get(identifier, None)
        elif object_type == ObjectType.GROUP:
            raw_object = self._groups.get(identifier, None)
        else:
            raise PersistenceError(
                f"The object type {object_type.name} is not supported by {self.__class__.__name__}."
            )
        if raw_object is None:
            raise ObjectNotFoundError(
                f"The {object_type.name} with the identifier '{identifier}' could not be found."
            )
        attributes = raw_object.get("attributes", {})
        if type(attributes) != dict:
            raise PersistenceError(
                f"The data of the object with type '{object_type.name}' and identifier "
                f"'{identifier}' is malformed and could not be loaded."
            )
        return PersistenceObject(
            object_type=object_type, id=identifier, attributes=attributes
        )

    def _load_static_data(self, data_file_path: str):
        """
        No good error handling here, since this is a dev-adapter and all exceptions
        are caught outside, when configuring.

        If we ever evolve this Adapter to production quality this has to change of course.
        """
        with open(data_file_path, "r") as fp:
            data = json.load(fp)
        self._users = data.get("users", {})
        self._groups = data.get("groups", {})
        if type(self._users) != dict or type(self._groups) != dict:
            raise RuntimeError("The json file did not contain the correct data.")
