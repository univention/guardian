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
    UDMPersistenceAdapterSettings,
)
from ..ports import PersistencePort
from ..udm_client import (  # type: ignore[attr-defined]
    UDM,
    NotFound,
    Object,
    Unauthorized,
    UnprocessableEntity,
)
from ..udm_client import (  # type: ignore[attr-defined]
    ConnectionError as UDMConnectionError,
)


class UDMPersistenceAdapter(PersistencePort, AsyncConfiguredAdapterMixin):
    """
    This adapter for the data storage queries a UDM REST API for the required objects.

    It expects the identifier of objects to be their DN in UDM.
    """

    class Config:
        is_cached = True
        alias = "udm_data"

    TYPE_MODULE_MAPPING = {
        ObjectType.GROUP: "groups/group",
        ObjectType.USER: "users/user",
    }

    def __init__(self):
        self._settings = None
        self._udm_client = None

    @property
    def udm_client(self):
        if self._udm_client is None:
            self._udm_client = UDM(
                self._settings.url, self._settings.username, self._settings.password
            )
        return self._udm_client

    async def configure(self, settings: UDMPersistenceAdapterSettings):
        self._settings = settings

    async def get_object(
        self, identifier: str, object_type: ObjectType
    ) -> PersistenceObject:
        module_name = self.TYPE_MODULE_MAPPING.get(object_type, "")
        local_logger = self.logger.bind(
            module_name=module_name, identifier=identifier, object_type=object_type
        )
        local_logger.debug("Fetching object from UDM.")
        if not module_name:
            raise PersistenceError(
                f"The object type '{object_type.name}' is not supported by {self.__class__.__name__}."
            )
        try:
            module = self.udm_client.get(module_name)
        except (NotFound, UDMConnectionError) as exc:
            raise PersistenceError(
                f"The UDM at '{self._settings.url}' could not be reached."
            ) from exc
        except Unauthorized as exc:
            raise PersistenceError(
                f"Could not authorize against UDM at '{self._settings.url}'."
            ) from exc
        except Exception as exc:
            raise PersistenceError(
                "An unexpected error occurred while fetching data from UDM."
            ) from exc
        try:
            raw_object: Object = module.get(identifier)
        except UnprocessableEntity as exc:
            raise ObjectNotFoundError(
                f"Could not find object of type '{object_type.name}' with identifier '{identifier}'."
            ) from exc
        result = PersistenceObject(
            id=raw_object.dn,
            object_type=object_type,
            attributes=raw_object.properties,
            roles=raw_object.properties.get("guardianRole", []),
        )
        local_logger.debug("Object retrieved from UDM.")
        return result

    @classmethod
    def get_settings_cls(
        cls,
    ) -> Type[UDMPersistenceAdapterSettings]:  # pragma: no cover
        return UDMPersistenceAdapterSettings


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
            object_type=object_type,
            id=identifier,
            attributes=attributes,
            roles=attributes.get("roles", []),
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
