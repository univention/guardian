# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict
from typing import Type

from port_loader import AsyncConfiguredAdapterMixin

from ..errors import ObjectNotFoundError, ParentNotFoundError
from ..models.base import PersistenceGetManyResult
from ..models.condition import Condition, ConditionGetQuery, ConditionsGetQuery
from ..models.sql_persistence import (
    DBApp,
    DBCondition,
    DBNamespace,
    SQLPersistenceAdapterSettings,
)
from ..ports.condition import ConditionPersistencePort
from .sql_persistence import SQLAlchemyMixin


class SQLConditionPersistenceAdapter(
    AsyncConfiguredAdapterMixin, ConditionPersistencePort, SQLAlchemyMixin
):
    @staticmethod
    def _condition_to_db_condition(
        condition: Condition, namespace_id: int
    ) -> DBCondition:
        return DBCondition(
            namespace_id=namespace_id,
            name=condition.name,
            display_name=condition.display_name,
            documentation=condition.documentation,
            parameters=",".join(condition.parameters),
            code=condition.code,
        )

    @staticmethod
    def _db_condition_to_condition(db_condition: DBCondition) -> Condition:
        return Condition(
            app_name=db_condition.namespace.app.name,
            namespace_name=db_condition.namespace.name,
            name=db_condition.name,
            display_name=db_condition.display_name,
            documentation=db_condition.documentation,
            parameters=[param for param in db_condition.parameters.split(",") if param],
            code=db_condition.code,
        )

    class Config:
        alias = "sql"
        cached = True

    @classmethod
    def get_settings_cls(
        cls,
    ) -> Type[SQLPersistenceAdapterSettings]:  # pragma: no cover
        return SQLPersistenceAdapterSettings

    async def configure(self, settings: SQLPersistenceAdapterSettings):
        self._db_string = SQLAlchemyMixin.create_db_string(**asdict(settings))

    async def create(self, condition: Condition) -> Condition:
        db_app = await self._get_single_object(DBApp, name=condition.app_name)
        if db_app is None:
            raise ParentNotFoundError(
                "The app of the object to be created does not exist."
            )
        db_namespace = await self._get_single_object(
            DBNamespace,
            app_name=db_app.name,
            name=condition.namespace_name,
        )
        if db_namespace is None:
            raise ParentNotFoundError(
                "The namespace of the object to be created does not exist."
            )
        async with self.session() as session:
            db_condition = SQLConditionPersistenceAdapter._condition_to_db_condition(
                condition, db_namespace.id
            )
            result = await self._create_object(db_condition, session=session)
        return SQLConditionPersistenceAdapter._db_condition_to_condition(result)

    async def read_one(self, query: ConditionGetQuery) -> Condition:
        result = await self._get_single_object(
            DBCondition,
            name=query.name,
            app_name=query.app_name,
            namespace_name=query.namespace_name,
        )
        if result is None:
            raise ObjectNotFoundError(
                f"No permission with the identifier '{query.app_name}:"
                f"{query.namespace_name}:{query.name}' could be found."
            )
        return SQLConditionPersistenceAdapter._db_condition_to_condition(result)

    async def read_many(
        self,
        query: ConditionsGetQuery,
    ) -> PersistenceGetManyResult[Condition]:
        dp_conditions, total_count = await self._get_many_objects(
            DBCondition,
            query.pagination.query_offset,
            query.pagination.query_limit,
            app_name=query.app_name,
            namespace_name=query.namespace_name,
        )
        conditions = [
            SQLConditionPersistenceAdapter._db_condition_to_condition(db_condition)
            for db_condition in dp_conditions
        ]
        return PersistenceGetManyResult(total_count=total_count, objects=conditions)

    async def update(self, condition: Condition) -> Condition:
        db_condition = await self._get_single_object(
            DBCondition,
            name=condition.name,
            app_name=condition.app_name,
            namespace_name=condition.namespace_name,
        )
        if db_condition is None:
            raise ObjectNotFoundError(
                f"No condition with the identifier '{condition.app_name}:"
                f"{condition.namespace_name}:{condition.name}' could be found."
            )
        modified = await self._update_object(
            db_condition,
            display_name=condition.display_name,
            documentation=condition.documentation,
            parameters=",".join(condition.parameters),
            code=condition.code,
        )
        return SQLConditionPersistenceAdapter._db_condition_to_condition(modified)
