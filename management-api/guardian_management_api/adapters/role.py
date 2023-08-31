# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict
from typing import Type

from port_loader import AsyncConfiguredAdapterMixin

from ..errors import ObjectNotFoundError, ParentNotFoundError
from ..models.base import PersistenceGetManyResult
from ..models.role import Role, RoleGetQuery, RolesGetQuery
from ..models.sql_persistence import (
    DBApp,
    DBNamespace,
    DBRole,
    SQLPersistenceAdapterSettings,
)
from ..ports.role import RolePersistencePort
from .sql_persistence import SQLAlchemyMixin


class SQLRolePersistenceAdapter(
    AsyncConfiguredAdapterMixin, RolePersistencePort, SQLAlchemyMixin
):
    @staticmethod
    def _role_to_db_role(role: Role, namespace_id: int) -> DBRole:
        return DBRole(
            namespace_id=namespace_id,
            name=role.name,
            display_name=role.display_name,
        )

    @staticmethod
    def _db_role_to_role(db_role: DBRole) -> Role:
        return Role(
            app_name=db_role.namespace.app.name,
            namespace_name=db_role.namespace.name,
            name=db_role.name,
            display_name=db_role.display_name,
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

    async def create(self, role: Role) -> Role:
        db_app = await self._get_single_object(DBApp, name=role.app_name)
        if db_app is None:
            raise ParentNotFoundError(
                "The app of the object to be created does not exist."
            )
        db_namespace = await self._get_single_object(
            DBNamespace,
            app_id=db_app.id,
            name=role.namespace_name,
        )
        if db_namespace is None:
            raise ParentNotFoundError(
                "The namespace of the object to be created does not exist."
            )
        async with self.session() as session:
            db_role = SQLRolePersistenceAdapter._role_to_db_role(role, db_namespace.id)
            result = await self._create_object(db_role, session=session)
        return SQLRolePersistenceAdapter._db_role_to_role(result)

    async def read_one(self, query: RoleGetQuery) -> Role | None:
        result = await self._get_single_object(DBRole, name=query.name)
        return SQLRolePersistenceAdapter._db_role_to_role(result) if result else None

    async def read_many(
        self,
        query: RolesGetQuery,
    ) -> PersistenceGetManyResult[Role]:
        total_count = await self._get_num_objects(DBRole)
        dp_roles = await self._get_many_objects(
            DBRole, query.pagination.query_offset, query.pagination.query_limit
        )
        roles = [
            SQLRolePersistenceAdapter._db_role_to_role(db_role) for db_role in dp_roles
        ]
        return PersistenceGetManyResult(total_count=total_count, objects=roles)

    async def update(self, role: Role) -> Role:
        db_role = await self._get_single_object(DBRole, name=role.name)
        if db_role is None:
            raise ObjectNotFoundError(
                f"No role with the identifier '{role.app_name}:"
                f"{role.namespace_name}:{role.name}' could be found."
            )
        modified = await self._update_object(db_role, display_name=role.display_name)
        return SQLRolePersistenceAdapter._db_role_to_role(modified)
