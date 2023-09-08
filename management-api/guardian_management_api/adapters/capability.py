# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict
from typing import Tuple, Type, Union

from port_loader import AsyncConfiguredAdapterMixin
from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from guardian_management_api.adapters.sql_persistence import (
    SQLAlchemyMixin,
    error_guard,
)
from guardian_management_api.errors import ObjectNotFoundError, ParentNotFoundError
from guardian_management_api.models.base import (
    PersistenceGetManyResult,
)
from guardian_management_api.models.capability import (
    CapabilitiesByRoleQuery,
    CapabilitiesGetQuery,
    Capability,
    CapabilityGetQuery,
    ParametrizedCondition,
)
from guardian_management_api.models.condition import Condition
from guardian_management_api.models.permission import Permission
from guardian_management_api.models.role import Role
from guardian_management_api.models.sql_persistence import (
    DBApp,
    DBCapability,
    DBCapabilityCondition,
    DBCondition,
    DBNamespace,
    DBPermission,
    DBRole,
    SQLPersistenceAdapterSettings,
)
from guardian_management_api.ports.capability import CapabilityPersistencePort


class SQLCapabilityPersistenceAdapter(
    AsyncConfiguredAdapterMixin, CapabilityPersistencePort, SQLAlchemyMixin
):
    class Config:
        alias = "sql"
        cached = True

    @staticmethod
    def _cap_to_db_cap(
        cap: Capability,
        namespace_id: int,
        role_id: int,
        db_permissions: list[DBPermission],
        db_conditions: list[DBCondition],
    ) -> DBCapability:
        sorted_conditions = sorted(
            cap.conditions, key=lambda x: f"{x.app_name}:{x.namespace_name}:{x.name}"
        )
        cap_conditions = set()
        for cond, db_cond in zip(sorted_conditions, db_conditions):
            cap_conditions.add(
                DBCapabilityCondition(condition_id=db_cond.id, kwargs=cond.parameters)
            )
        return DBCapability(
            namespace_id=namespace_id,
            name=cap.name,
            display_name=cap.display_name,
            role_id=role_id,
            relation=cap.relation,
            permissions=set(db_permissions),
            conditions=cap_conditions,
        )

    @staticmethod
    def _db_cap_to_cap(db_cap: DBCapability) -> Capability:
        return Capability(
            app_name=db_cap.namespace.app.name,
            namespace_name=db_cap.namespace.name,
            name=db_cap.name,
            display_name=db_cap.display_name,
            role=Role(
                app_name=db_cap.role.namespace.app.name,
                namespace_name=db_cap.role.namespace.name,
                name=db_cap.role.name,
            ),
            permissions=[
                Permission(
                    app_name=perm.namespace.app.name,
                    namespace_name=perm.namespace.name,
                    name=perm.name,
                )
                for perm in db_cap.permissions
            ],
            relation=db_cap.relation,
            conditions=[
                ParametrizedCondition(
                    app_name=cap_cond.condition.namespace.app.name,
                    namespace_name=cap_cond.condition.namespace.name,
                    name=cap_cond.condition.name,
                    parameters=cap_cond.kwargs,
                )
                for cap_cond in db_cap.conditions
            ],
        )

    @classmethod
    def get_settings_cls(
        cls,
    ) -> Type[SQLPersistenceAdapterSettings]:  # pragma: no cover
        return SQLPersistenceAdapterSettings

    async def configure(self, settings: SQLPersistenceAdapterSettings):
        self._db_string = SQLAlchemyMixin.create_db_string(**asdict(settings))

    @SQLAlchemyMixin.session_wrapper
    async def _get_db_child_objs_for_capability(
        self,
        obj_type: Type[DBPermission | DBCondition],
        objs: list[Permission | ParametrizedCondition],
        *,
        session: AsyncSession,
    ) -> list[DBPermission | DBCondition]:
        objs_identifiers = [
            (obj.app_name, obj.namespace_name, obj.name) for obj in objs
        ]
        stmt = (
            select(obj_type)
            .order_by(DBApp.name, DBNamespace.name, obj_type.name)
            .join(DBNamespace, obj_type.namespace_id == DBNamespace.id)  # type: ignore[arg-type]
            .join(DBApp, DBNamespace.app_id == DBApp.id)  # type: ignore[arg-type]
            .where(
                tuple_(DBApp.name, DBNamespace.name, obj_type.name).in_(  # type: ignore[arg-type]
                    objs_identifiers
                )
            )
        )
        result = list((await session.scalars(stmt)).all())
        if len(result) != len(objs):
            raise ObjectNotFoundError(
                f"Not all {'permissions' if obj_type is DBPermission else 'contexts'} "
                f"specified for the capability could be found.",
                object_type=Permission if obj_type is DBPermission else Condition,
            )
        return result  # type: ignore[return-value]

    async def create(self, obj: Capability) -> Capability:
        db_namespace = await self._get_single_object(
            DBNamespace, app_name=obj.app_name, name=obj.namespace_name
        )
        if db_namespace is None:
            raise ParentNotFoundError(
                "The namespace of the capability to create does not exist."
            )
        db_role = await self._get_single_object(
            DBRole,
            app_name=obj.role.app_name,
            namespace_name=obj.role.namespace_name,
            name=obj.role.name,
        )
        if db_role is None:
            raise ObjectNotFoundError(
                "The capabilities role could not be found.", object_type=Role
            )
        async with self.session() as session:
            permissions: list[
                DBPermission
            ] = await self._get_db_child_objs_for_capability(
                DBPermission, obj.permissions, session=session
            )
            conditions: list[
                DBCondition
            ] = await self._get_db_child_objs_for_capability(
                DBCondition, obj.conditions, session=session
            )
        db_cap = SQLCapabilityPersistenceAdapter._cap_to_db_cap(
            obj, db_namespace.id, db_role.id, permissions, conditions
        )
        result = await self._create_object(db_cap)
        return SQLCapabilityPersistenceAdapter._db_cap_to_cap(result)

    async def update(self, obj: Capability) -> Capability:
        # This can probably be implemented without deleting objects, but since there
        # is currently no disadvantage, this is the easiest way to implement this.
        await self.delete(
            CapabilityGetQuery(
                app_name=obj.app_name, namespace_name=obj.namespace_name, name=obj.name
            )
        )
        return await self.create(obj)

    async def delete(self, query: CapabilityGetQuery) -> None:
        db_capability = await self._get_single_object(
            DBCapability,
            name=query.name,
            app_name=query.app_name,
            namespace_name=query.namespace_name,
        )
        if db_capability is None:
            raise ObjectNotFoundError(
                f"No capability with the identifier '{query.app_name}:"
                f"{query.namespace_name}:{query.name}' could be found.",
                object_type=Capability,
            )
        await self._delete_obj(db_capability)

    async def read_one(self, query: CapabilityGetQuery) -> Capability:
        result = await self._get_single_object(
            DBCapability,
            name=query.name,
            app_name=query.app_name,
            namespace_name=query.namespace_name,
        )
        if result is None:
            raise ObjectNotFoundError(
                f"No capability with the identifier '{query.app_name}:"
                f"{query.namespace_name}:{query.name}' could be found.",
                object_type=Capability,
            )
        return SQLCapabilityPersistenceAdapter._db_cap_to_cap(result)

    @staticmethod
    def _configure_search_stmt_by_role(
        stmt, app_name: str, namespace_name: str, name: str
    ):
        return (
            stmt.join(DBRole, DBCapability.role_id == DBRole.id)
            .join(DBNamespace, DBRole.namespace_id == DBNamespace.id)
            .join(DBApp, DBNamespace.app_id == DBApp.id)
            .where(
                DBApp.name == app_name,
                DBNamespace.name == namespace_name,
                DBRole.name == name,
            )
        )

    @error_guard
    @SQLAlchemyMixin.session_wrapper
    async def _get_capabilities_by_role(
        self, query: CapabilitiesByRoleQuery, *, session: AsyncSession
    ) -> Tuple[list[DBCapability], int]:
        select_stmt = (
            select(DBCapability)
            .offset(query.pagination.query_offset)
            .order_by(DBCapability.name)
        )
        count_stmt = select(count(DBCapability.id))
        if query.pagination.query_limit:
            select_stmt = select_stmt.limit(query.pagination.query_limit)
        select_stmt = SQLCapabilityPersistenceAdapter._configure_search_stmt_by_role(
            select_stmt, query.app_name, query.namespace_name, query.role_name
        )
        count_stmt = SQLCapabilityPersistenceAdapter._configure_search_stmt_by_role(
            count_stmt, query.app_name, query.namespace_name, query.role_name
        )
        return (
            list((await session.scalars(select_stmt)).unique().all()),
            await session.scalar(count_stmt),  # type: ignore[return-value]
        )

    async def read_many(
        self, query: Union[CapabilitiesGetQuery, CapabilitiesByRoleQuery]
    ) -> PersistenceGetManyResult[Capability]:
        if isinstance(query, CapabilitiesGetQuery):
            db_conditions, total_count = await self._get_many_objects(
                DBCapability,
                query.pagination.query_offset,
                query.pagination.query_limit,
                app_name=query.app_name,
                namespace_name=query.namespace_name,
            )
        elif isinstance(query, CapabilitiesByRoleQuery):
            db_conditions, total_count = await self._get_capabilities_by_role(query)
        else:
            raise RuntimeError("Unknown query type.")
        capabilities = [
            SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
            for db_cap in db_conditions
        ]
        return PersistenceGetManyResult(total_count=total_count, objects=capabilities)
