import json
from typing import Any, Iterable

from .errors import PersistenceError, ObjectNotFoundError
from .models.ports import ObjectType, PersistenceObject, RequiredSetting
from .ports import PersistencePort


class StaticDataAdapter(PersistencePort):
    """
    This adapter for the PersistencePort implements a data store that is held in memory and
    seeded by a json file that is loaded from the path configured by 'static_data_adapter.data_file'.

    This adapter is not meant for production but rather for testing purposes.
    """

    DATA_FILE_SETTING_NAME = "static_data_adapter.data_file"

    def __init__(self, logger):
        super().__init__(logger)
        self._users = dict()
        self._groups = dict()

    @property
    def is_cached(self):
        return True

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

    @staticmethod
    def required_settings() -> Iterable[RequiredSetting]:
        return [RequiredSetting(StaticDataAdapter.DATA_FILE_SETTING_NAME, str, None)]

    async def configure(self, settings: dict[str, Any]):
        self._load_static_data(settings[StaticDataAdapter.DATA_FILE_SETTING_NAME])
