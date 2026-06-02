# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict
from typing import Optional, Type, Union

from port_loader import AsyncConfiguredAdapterMixin
from sqlalchemy import select, tuple_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import COMPLETE_URL
from ..errors import ObjectNotFoundError, ParentNotFoundError
from ..models.base import PaginationRequest, PersistenceGetManyResult
from ..models.capability import CapabilityReference
from ..models.role import (
    Role,
    RoleCreateQuery,
    RoleGetQuery,
    RolesGetQuery,
)
from ..models.routers.base import ManagementObjectName, PaginationInfo
from ..models.routers.role import (
    Role as ResponseRole,
)
from ..models.routers.role import (
    RoleCapability,
    RoleCreateRequest,
    RoleGetAllRequest,
    RoleGetByAppRequest,
    RoleGetFullIdentifierRequest,
    RoleMultipleResponse,
    RoleSingleResponse,
)
from ..models.sql_persistence import (
    DBApp,
    DBCapability,
    DBNamespace,
    DBRole,
    SQLPersistenceAdapterSettings,
)
from ..ports.role import (
    RoleAPIPort,
    RolePersistencePort,
)
from .fastapi_utils import TransformExceptionMixin
from .sql_persistence import SQLAlchemyMixin


class TransformRoleExceptionMixin(TransformExceptionMixin): ...


class FastAPIRoleAPIAdapter(
    TransformRoleExceptionMixin,
    RoleAPIPort[
        RoleCreateRequest,
        RoleSingleResponse,
        RoleGetFullIdentifierRequest,
        RoleSingleResponse,
        Union[RoleGetAllRequest, RoleGetByAppRequest],
        RoleMultipleResponse,
    ],
):
    class Config:
        alias = "fastapi"

    @staticmethod
    def _capability_refs(role: Role) -> list[RoleCapability]:
        return [
            RoleCapability(
                app_name=ManagementObjectName(cap.app_name),
                namespace_name=ManagementObjectName(cap.namespace_name),
                name=ManagementObjectName(cap.name),
            )
            for cap in role.capabilities
        ]

    async def to_role_create(self, api_request: RoleCreateRequest) -> RoleCreateQuery:
        return RoleCreateQuery(
            roles=[
                Role(
                    app_name=api_request.app_name,
                    name=api_request.data.name,
                    display_name=api_request.data.display_name,
                    capabilities=[
                        cap.to_reference() for cap in api_request.data.capabilities
                    ],
                )
            ]
        )

    async def to_role_create_response(self, role_result: Role) -> RoleSingleResponse:
        return RoleSingleResponse(
            role=ResponseRole(
                app_name=role_result.app_name,
                name=role_result.name,
                display_name=(
                    role_result.display_name if role_result.display_name else ""
                ),
                resource_url=f"{COMPLETE_URL}/roles/{role_result.app_name}/{role_result.name}",
                capabilities=self._capability_refs(role_result),
            )
        )

    async def to_role_get(
        self, api_request: RoleGetFullIdentifierRequest
    ) -> RoleGetQuery:
        return RoleGetQuery(
            app_name=api_request.app_name,
            name=api_request.name,
        )

    async def to_role_get_response(self, role_result: Role) -> RoleSingleResponse:
        return RoleSingleResponse(
            role=ResponseRole(
                app_name=role_result.app_name,
                name=role_result.name,
                display_name=role_result.display_name,
                resource_url=f"{COMPLETE_URL}/roles/{role_result.app_name}/{role_result.name}",
                capabilities=self._capability_refs(role_result),
            )
        )

    async def to_roles_get(
        self,
        api_request: RoleGetAllRequest | RoleGetByAppRequest,
    ) -> RolesGetQuery:
        return RolesGetQuery(
            app_name=getattr(api_request, "app_name", None),
            pagination=PaginationRequest(
                query_offset=api_request.offset, query_limit=api_request.limit
            ),
        )

    async def to_roles_get_response(
        self,
        roles: list[Role],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> RoleMultipleResponse:
        return RoleMultipleResponse(
            pagination=PaginationInfo(
                offset=query_offset,
                limit=query_limit,
                total_count=total_count,
            ),
            roles=[
                ResponseRole(
                    app_name=role.app_name,
                    name=role.name,
                    display_name=role.display_name,
                    resource_url=f"{COMPLETE_URL}/roles/{role.app_name}/{role.name}",
                    capabilities=self._capability_refs(role),
                )
                for role in roles
            ],
        )

    async def to_role_edit(
        self,
        old_role: Role,
        display_name: Optional[str] = None,
        capabilities: Optional[list[CapabilityReference]] = None,
    ) -> Role:
        new_display_name = (
            display_name if display_name is not None else old_role.display_name
        )
        new_capabilities = (
            list(old_role.capabilities) if capabilities is None else list(capabilities)
        )
        return Role(
            app_name=old_role.app_name,
            name=old_role.name,
            display_name=new_display_name,
            capabilities=new_capabilities,
        )


class SQLRolePersistenceAdapter(
    AsyncConfiguredAdapterMixin, RolePersistencePort, SQLAlchemyMixin
):
    @staticmethod
    def _db_role_to_role(db_role: DBRole) -> Role:
        return Role(
            app_name=db_role.app.name,
            name=db_role.name,
            display_name=db_role.display_name,
            is_builtin=db_role.is_builtin,
            capabilities=[
                CapabilityReference(
                    app_name=db_cap.namespace.app.name,
                    namespace_name=db_cap.namespace.name,
                    name=db_cap.name,
                )
                for db_cap in db_role.capability
            ],
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

    @SQLAlchemyMixin.session_wrapper
    async def _resolve_capability_refs(
        self,
        capabilities: list[CapabilityReference],
        *,
        session: AsyncSession,
    ) -> list[DBCapability]:
        if not capabilities:
            return []
        identifiers = [
            (cap.app_name, cap.namespace_name, cap.name) for cap in capabilities
        ]
        stmt = (
            select(DBCapability)
            .join(DBNamespace, DBCapability.namespace_id == DBNamespace.id)
            .join(DBApp, DBNamespace.app_id == DBApp.id)
            .where(
                tuple_(DBApp.name, DBNamespace.name, DBCapability.name).in_(identifiers)
            )
        )
        result = list((await session.scalars(stmt)).unique().all())
        if len(result) != len(set(identifiers)):
            raise ObjectNotFoundError(
                "Not all capabilities specified for the role could be found.",
                object_type=CapabilityReference,
            )
        return result

    async def create(self, role: Role) -> Role:
        db_app = await self._get_single_object(DBApp, name=role.app_name)
        if db_app is None:
            raise ParentNotFoundError(
                "The app of the object to be created does not exist."
            )
        async with self.session() as session:
            try:
                async with session.begin():
                    db_capabilities = await self._resolve_capability_refs(
                        role.capabilities, session=session
                    )
                    db_role = DBRole(
                        app_id=db_app.id,
                        name=role.name,
                        display_name=role.display_name,
                        capability=set(db_capabilities),
                    )
                    session.add(db_role)
            except IntegrityError as exc:
                self._translate_integrity_error(exc)
            await session.refresh(db_role)
        return SQLRolePersistenceAdapter._db_role_to_role(db_role)

    async def read_one(self, query: RoleGetQuery) -> Role:
        result = await self._get_single_object(
            DBRole,
            name=query.name,
            app_name=query.app_name,
        )
        if result is None:
            raise ObjectNotFoundError(
                f"No role with the identifier '{query.app_name}:{query.name}' could be found."
            )
        return SQLRolePersistenceAdapter._db_role_to_role(result)

    async def read_many(
        self,
        query: RolesGetQuery,
    ) -> PersistenceGetManyResult[Role]:
        db_roles, total_count = await self._get_many_objects(
            DBRole,
            query.pagination.query_offset,
            query.pagination.query_limit,
            app_name=query.app_name,
        )
        roles = [
            SQLRolePersistenceAdapter._db_role_to_role(db_role) for db_role in db_roles
        ]
        return PersistenceGetManyResult(total_count=total_count, objects=roles)

    async def update(self, role: Role) -> Role:
        db_role = await self._get_single_object(
            DBRole,
            name=role.name,
            app_name=role.app_name,
        )
        if db_role is None:
            raise ObjectNotFoundError(
                f"No role with the identifier '{role.app_name}:{role.name}' could be found."
            )
        async with self.session() as session:
            try:
                async with session.begin():
                    db_capabilities = await self._resolve_capability_refs(
                        role.capabilities, session=session
                    )
                    merged_role = await session.merge(db_role)
                    merged_role.display_name = role.display_name
                    merged_role.capability = set(db_capabilities)
                    session.add(merged_role)
            except IntegrityError as exc:
                self._translate_integrity_error(exc)
            await session.refresh(merged_role)
        return SQLRolePersistenceAdapter._db_role_to_role(merged_role)

    async def delete(self, query: RoleGetQuery) -> None:
        db_role = await self._get_single_object(
            DBRole,
            name=query.name,
            app_name=query.app_name,
        )
        if db_role is None:
            raise ObjectNotFoundError(
                f"No role with the identifier '{query.app_name}:{query.name}' could be found.",
                object_type=Role,
            )
        await self._delete_obj(db_role)

    async def read_dependencies(self, query: RoleGetQuery) -> list[CapabilityReference]:
        db_role = await self._get_single_object(
            DBRole,
            name=query.name,
            app_name=query.app_name,
        )
        if db_role is None:
            raise ObjectNotFoundError(
                f"No role with the identifier '{query.app_name}:{query.name}' could be found.",
                object_type=Role,
            )
        return [
            CapabilityReference(
                app_name=db_cap.namespace.app.name,
                namespace_name=db_cap.namespace.name,
                name=db_cap.name,
            )
            for db_cap in db_role.capability
        ]
