# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict
from typing import Type

from port_loader import AsyncConfiguredAdapterMixin

from ..errors import ObjectNotFoundError, ParentNotFoundError
from ..models.base import PersistenceGetManyResult
from ..models.permission import Permission, PermissionGetQuery, PermissionsGetQuery
from ..models.sql_persistence import (
    DBApp,
    DBNamespace,
    DBPermission,
    SQLPersistenceAdapterSettings,
)
from ..ports.permission import PermissionPersistencePort
from .sql_persistence import SQLAlchemyMixin


class SQLPermissionPersistenceAdapter(
    AsyncConfiguredAdapterMixin, PermissionPersistencePort, SQLAlchemyMixin
):
    @staticmethod
    def _permission_to_db_permission(
        permission: Permission, namespace_id: int
    ) -> DBPermission:
        return DBPermission(
            namespace_id=namespace_id,
            name=permission.name,
            display_name=permission.display_name,
        )

    @staticmethod
    def _db_permission_to_permission(db_permission: DBPermission) -> Permission:
        return Permission(
            app_name=db_permission.namespace.app.name,
            namespace_name=db_permission.namespace.name,
            name=db_permission.name,
            display_name=db_permission.display_name,
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

    async def create(self, permission: Permission) -> Permission:
        db_app = await self._get_single_object(DBApp, name=permission.app_name)
        if db_app is None:
            raise ParentNotFoundError(
                "The app of the object to be created does not exist."
            )
        db_namespace = await self._get_single_object(
            DBNamespace,
            app_id=db_app.id,
            name=permission.namespace_name,
        )
        if db_namespace is None:
            raise ParentNotFoundError(
                "The namespace of the object to be created does not exist."
            )
        async with self.session() as session:
            db_permission = (
                SQLPermissionPersistenceAdapter._permission_to_db_permission(
                    permission, db_namespace.id
                )
            )
            result = await self._create_object(db_permission, session=session)
        return SQLPermissionPersistenceAdapter._db_permission_to_permission(result)

    async def read_one(self, query: PermissionGetQuery) -> Permission:
        result = await self._get_single_object(DBPermission, name=query.name)
        if result is None:
            raise ObjectNotFoundError(
                f"No permission with the identifier '{query.app_name}:"
                f"{query.namespace_name}:{query.name}' could be found."
            )
        return SQLPermissionPersistenceAdapter._db_permission_to_permission(result)

    async def read_many(
        self,
        query: PermissionsGetQuery,
    ) -> PersistenceGetManyResult[Permission]:
        total_count = await self._get_num_objects(DBPermission)
        dp_permissions = await self._get_many_objects(
            DBPermission, query.pagination.query_offset, query.pagination.query_limit
        )
        permissions = [
            SQLPermissionPersistenceAdapter._db_permission_to_permission(db_permission)
            for db_permission in dp_permissions
        ]
        return PersistenceGetManyResult(total_count=total_count, objects=permissions)

    async def update(self, permission: Permission) -> Permission:
        db_permission = await self._get_single_object(
            DBPermission, name=permission.name
        )
        if db_permission is None:
            raise ObjectNotFoundError(
                f"No permission with the identifier '{permission.app_name}:"
                f"{permission.namespace_name}:{permission.name}' could be found."
            )
        modified = await self._update_object(
            db_permission, display_name=permission.display_name
        )
        return SQLPermissionPersistenceAdapter._db_permission_to_permission(modified)
