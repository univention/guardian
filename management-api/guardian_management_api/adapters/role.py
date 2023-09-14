# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict
from typing import Optional, Type, Union

from fastapi import HTTPException
from port_loader import AsyncConfiguredAdapterMixin
from starlette import status

from ..constants import COMPLETE_URL
from ..errors import ObjectNotFoundError, ParentNotFoundError
from ..models.base import PaginationRequest, PersistenceGetManyResult
from ..models.role import (
    Role,
    RoleCreateQuery,
    RoleGetQuery,
    RolesGetQuery,
)
from ..models.routers.base import PaginationInfo
from ..models.routers.role import (
    Role as ResponseRole,
)
from ..models.routers.role import (
    RoleCreateRequest,
    RoleGetAllRequest,
    RoleGetByAppRequest,
    RoleGetByNamespaceRequest,
    RoleGetFullIdentifierRequest,
    RoleMultipleResponse,
    RoleSingleResponse,
)
from ..models.sql_persistence import (
    DBApp,
    DBNamespace,
    DBRole,
    SQLPersistenceAdapterSettings,
)
from ..ports.role import (
    RoleAPIPort,
    RolePersistencePort,
)
from .sql_persistence import SQLAlchemyMixin


class FastAPIRoleAPIAdapter(
    RoleAPIPort[
        RoleCreateRequest,
        RoleSingleResponse,
        RoleGetFullIdentifierRequest,
        RoleSingleResponse,
        Union[RoleGetAllRequest, RoleGetByAppRequest, RoleGetByNamespaceRequest],
        RoleMultipleResponse,
    ]
):
    class Config:
        alias = "fastapi"

    async def transform_exception(self, exc: Exception) -> Exception:
        if isinstance(exc, ObjectNotFoundError):
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "App not found."},
            )
        elif isinstance(exc, ParentNotFoundError):
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": str(exc)},
            )
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal Server Error"},
        )

    async def to_role_create(self, api_request: RoleCreateRequest) -> RoleCreateQuery:
        return RoleCreateQuery(
            roles=[
                Role(
                    app_name=api_request.app_name,
                    namespace_name=api_request.namespace_name,
                    name=api_request.data.name,
                    display_name=api_request.data.display_name,
                )
            ]
        )

    async def to_role_create_response(self, role_result: Role) -> RoleSingleResponse:
        return RoleSingleResponse(
            role=ResponseRole(
                app_name=role_result.app_name,
                namespace_name=role_result.namespace_name,
                name=role_result.name,
                display_name=role_result.display_name
                if role_result.display_name
                else "",
                resource_url=f"{COMPLETE_URL}/roles/{role_result.app_name}/{role_result.namespace_name}/{role_result.name}",
            )
        )

    async def to_role_get(
        self, api_request: RoleGetFullIdentifierRequest
    ) -> RoleGetQuery:
        return RoleGetQuery(
            app_name=api_request.app_name,
            namespace_name=api_request.namespace_name,
            name=api_request.name,
        )

    async def to_role_get_response(self, role_result: Role) -> RoleSingleResponse:
        return RoleSingleResponse(
            role=ResponseRole(
                app_name=role_result.app_name,
                namespace_name=role_result.namespace_name,
                name=role_result.name,
                display_name=role_result.display_name,
                resource_url=f"{COMPLETE_URL}/roles/{role_result.app_name}/{role_result.namespace_name}/{role_result.name}",
            )
        )

    async def to_roles_get(
        self,
        api_request: Union[
            RoleGetAllRequest, RoleGetByAppRequest, RoleGetByNamespaceRequest
        ],
    ) -> RolesGetQuery:
        return RolesGetQuery(
            app_name=getattr(api_request, "app_name", None),
            namespace_name=getattr(api_request, "namespace_name", None),
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
                    namespace_name=role.namespace_name,
                    name=role.name,
                    display_name=role.display_name,
                    resource_url=f"{COMPLETE_URL}/roles/{role.app_name}/{role.namespace_name}/{role.name}",
                )
                for role in roles
            ],
        )

    async def to_role_edit(self, old_role: Role, display_name: Optional[str]) -> Role:
        return Role(
            app_name=old_role.app_name,
            namespace_name=old_role.namespace_name,
            name=old_role.name,
            display_name=display_name,
        )


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
            app_name=db_app.name,
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

    async def read_one(self, query: RoleGetQuery) -> Role:
        result = await self._get_single_object(
            DBRole,
            name=query.name,
            app_name=query.app_name,
            namespace_name=query.namespace_name,
        )
        if result is None:
            raise ObjectNotFoundError(
                f"No role with the identifier '{query.app_name}:"
                f"{query.namespace_name}:{query.name}' could be found."
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
            namespace_name=query.namespace_name,
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
            namespace_name=role.namespace_name,
        )
        if db_role is None:
            raise ObjectNotFoundError(
                f"No role with the identifier '{role.app_name}:"
                f"{role.namespace_name}:{role.name}' could be found."
            )
        modified = await self._update_object(db_role, display_name=role.display_name)
        return SQLRolePersistenceAdapter._db_role_to_role(modified)
