from typing import Any, Iterable

from .models.ports import ObjectType, PersistenceObject, RequiredSetting
from .ports import PersistencePort


class StaticData(PersistencePort):
    @property
    def is_singleton(self):
        return True

    async def get_object(
        self, identifier: str, object_type: ObjectType
    ) -> PersistenceObject:
        raise NotImplementedError

    @staticmethod
    def required_settings() -> Iterable[RequiredSetting]:
        return []

    async def configure(self, settings: dict[str, Any]):
        pass
