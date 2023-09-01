# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict
from typing import Type

from port_loader import AsyncConfiguredAdapterMixin

from ..errors import ObjectNotFoundError, ParentNotFoundError
from ..models.base import PersistenceGetManyResult
from ..models.context import Context, ContextGetQuery, ContextsGetQuery
from ..models.sql_persistence import (
    DBApp,
    DBContext,
    DBNamespace,
    SQLPersistenceAdapterSettings,
)
from ..ports.context import ContextPersistencePort
from .sql_persistence import SQLAlchemyMixin


class SQLContextPersistenceAdapter(
    AsyncConfiguredAdapterMixin, ContextPersistencePort, SQLAlchemyMixin
):
    @staticmethod
    def _context_to_db_context(context: Context, namespace_id: int) -> DBContext:
        return DBContext(
            namespace_id=namespace_id,
            name=context.name,
            display_name=context.display_name,
        )

    @staticmethod
    def _db_context_to_context(db_context: DBContext) -> Context:
        return Context(
            app_name=db_context.namespace.app.name,
            namespace_name=db_context.namespace.name,
            name=db_context.name,
            display_name=db_context.display_name,
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

    async def create(self, context: Context) -> Context:
        db_app = await self._get_single_object(DBApp, name=context.app_name)
        if db_app is None:
            raise ParentNotFoundError(
                "The app of the object to be created does not exist."
            )
        db_namespace = await self._get_single_object(
            DBNamespace,
            app_id=db_app.id,
            name=context.namespace_name,
        )
        if db_namespace is None:
            raise ParentNotFoundError(
                "The namespace of the object to be created does not exist."
            )
        async with self.session() as session:
            db_context = SQLContextPersistenceAdapter._context_to_db_context(
                context, db_namespace.id
            )
            result = await self._create_object(db_context, session=session)
        return SQLContextPersistenceAdapter._db_context_to_context(result)

    async def read_one(self, query: ContextGetQuery) -> Context | None:
        result = await self._get_single_object(DBContext, name=query.name)
        return (
            SQLContextPersistenceAdapter._db_context_to_context(result)
            if result
            else None
        )

    async def read_many(
        self,
        query: ContextsGetQuery,
    ) -> PersistenceGetManyResult[Context]:
        total_count = await self._get_num_objects(DBContext)
        dp_contexts = await self._get_many_objects(
            DBContext, query.pagination.query_offset, query.pagination.query_limit
        )
        contexts = [
            SQLContextPersistenceAdapter._db_context_to_context(db_context)
            for db_context in dp_contexts
        ]
        return PersistenceGetManyResult(total_count=total_count, objects=contexts)

    async def update(self, context: Context) -> Context:
        db_context = await self._get_single_object(DBContext, name=context.name)
        if db_context is None:
            raise ObjectNotFoundError(
                f"No context with the identifier '{context.app_name}:"
                f"{context.namespace_name}:{context.name}' could be found."
            )
        modified = await self._update_object(
            db_context, display_name=context.display_name
        )
        return SQLContextPersistenceAdapter._db_context_to_context(modified)
