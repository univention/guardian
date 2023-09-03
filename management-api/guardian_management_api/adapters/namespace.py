# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict
from typing import Type

from port_loader import AsyncConfiguredAdapterMixin

from ..errors import ObjectNotFoundError, ParentNotFoundError
from ..models.base import PersistenceGetManyResult
from ..models.namespace import Namespace, NamespaceGetQuery, NamespacesGetQuery
from ..models.sql_persistence import DBApp, DBNamespace, SQLPersistenceAdapterSettings
from ..ports.namespace import NamespacePersistencePort
from .sql_persistence import SQLAlchemyMixin


class SQLNamespacePersistenceAdapter(
    AsyncConfiguredAdapterMixin, NamespacePersistencePort, SQLAlchemyMixin
):
    @staticmethod
    def _namespace_to_db_namespace(namespace: Namespace, app_id: int) -> DBNamespace:
        return DBNamespace(
            app_id=app_id, name=namespace.name, display_name=namespace.display_name
        )

    @staticmethod
    def _db_namespace_to_namespace(db_namespace: DBNamespace) -> Namespace:
        return Namespace(
            name=db_namespace.name,
            display_name=db_namespace.display_name,
            app_name=db_namespace.app.name,
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

    async def create(self, namespace: Namespace) -> Namespace:
        db_app = await self._get_single_object(DBApp, name=namespace.app_name)
        if db_app is None:
            raise ParentNotFoundError(
                "The app/namespace of the object to be created does not exist."
            )
        async with self.session() as session:
            db_ns = SQLNamespacePersistenceAdapter._namespace_to_db_namespace(
                namespace, db_app.id
            )
            result = await self._create_object(db_ns, session=session)
        return SQLNamespacePersistenceAdapter._db_namespace_to_namespace(result)

    async def read_one(self, query: NamespaceGetQuery) -> Namespace:
        result = await self._get_single_object(DBNamespace, name=query.name)
        if result is None:
            raise ObjectNotFoundError(
                f"No namespace with the identifier '{query.app_name}:"
                f"{query.name}' could be found."
            )
        return SQLNamespacePersistenceAdapter._db_namespace_to_namespace(result)

    async def read_many(
        self,
        query: NamespacesGetQuery,
    ) -> PersistenceGetManyResult[Namespace]:
        total_count = await self._get_num_objects(DBNamespace)
        dp_namespaces = await self._get_many_objects(
            DBNamespace,
            query.pagination.query_offset,
            query.pagination.query_limit,
            app_name=query.app_name,
        )
        namespaces = [
            SQLNamespacePersistenceAdapter._db_namespace_to_namespace(db_app)
            for db_app in dp_namespaces
        ]
        return PersistenceGetManyResult(total_count=total_count, objects=namespaces)

    async def update(self, namespace: Namespace) -> Namespace:
        db_app = await self._get_single_object(DBNamespace, name=namespace.name)
        if db_app is None:
            raise ObjectNotFoundError(
                f"No app with the identifier '{namespace.app_name}:{namespace.name}' could be found."
            )
        modified = await self._update_object(
            db_app, display_name=namespace.display_name
        )
        return SQLNamespacePersistenceAdapter._db_namespace_to_namespace(modified)
