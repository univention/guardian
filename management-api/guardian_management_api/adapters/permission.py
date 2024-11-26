# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict
from typing import Any, List, Optional, Type

from port_loader import AsyncConfiguredAdapterMixin

from ..constants import COMPLETE_URL
from ..errors import ObjectNotFoundError, ParentNotFoundError
from ..models.base import PaginationRequest, PersistenceGetManyResult
from ..models.permission import (
    Permission,
    PermissionCreateQuery,
    PermissionGetQuery,
    PermissionsGetQuery,
)
from ..models.routers.base import (
    GetAllRequest,
    GetByAppRequest,
    GetByNamespaceRequest,
    ManagementObjectName,
    PaginationInfo,
)
from ..models.routers.permission import FastAPIPermission as ResponsePermission
from ..models.routers.permission import (
    PermissionCreateRequest,
    PermissionEditRequest,
    PermissionGetRequest,
    PermissionMultipleResponse,
    PermissionSingleResponse,
)
from ..models.sql_persistence import (
    DBApp,
    DBNamespace,
    DBPermission,
    SQLPersistenceAdapterSettings,
)
from ..ports.permission import (
    PermissionAPIPort,
    PermissionPersistencePort,
)
from .fastapi_utils import TransformExceptionMixin
from .sql_persistence import SQLAlchemyMixin


class TransformPermissionExceptionMixin(TransformExceptionMixin): ...


class FastAPIPermissionAPIAdapter(
    TransformPermissionExceptionMixin,
    PermissionAPIPort[
        PermissionGetRequest,
        PermissionSingleResponse,
        GetAllRequest | GetByAppRequest | GetByNamespaceRequest,
        PermissionMultipleResponse,
        PermissionCreateRequest,
        PermissionEditRequest,
    ],
):
    class Config:
        alias = "fastapi"

    async def to_obj_get_single(
        self, api_request: PermissionGetRequest
    ) -> PermissionGetQuery:
        return PermissionGetQuery(
            name=api_request.name,
            app_name=api_request.app_name,
            namespace_name=api_request.namespace_name,
        )

    async def to_obj_get_multiple(
        self, api_request: GetAllRequest | GetByAppRequest | GetByNamespaceRequest
    ) -> PermissionsGetQuery:
        return PermissionsGetQuery(
            pagination=PaginationRequest(
                query_offset=api_request.offset, query_limit=api_request.limit
            ),
            app_name=getattr(api_request, "app_name", None),
            namespace_name=getattr(api_request, "namespace_name", None),
        )

    async def to_obj_create(
        self, api_request: PermissionCreateRequest
    ) -> PermissionCreateQuery:
        return PermissionCreateQuery(
            permissions=[
                Permission(
                    name=api_request.data.name,
                    display_name=api_request.data.display_name,
                    app_name=api_request.app_name,
                    namespace_name=api_request.namespace_name,
                )
            ]
        )

    async def to_obj_edit(
        self, api_request: PermissionEditRequest
    ) -> tuple[PermissionGetQuery, dict[str, Any]]:
        query = PermissionGetQuery(
            app_name=api_request.app_name,
            namespace_name=api_request.namespace_name,
            name=api_request.name,
        )
        changed_data = api_request.data.dict(exclude_unset=True)
        return query, changed_data

    async def to_api_get_single_response(
        self, obj: Permission
    ) -> PermissionSingleResponse:
        return PermissionSingleResponse(
            permission=ResponsePermission(
                name=ManagementObjectName(obj.name),
                display_name=obj.display_name,
                app_name=ManagementObjectName(obj.app_name),
                namespace_name=ManagementObjectName(obj.namespace_name),
                resource_url=f"{COMPLETE_URL}/permissions/{obj.app_name}/{obj.namespace_name}/{obj.name}",
            )
        )

    async def to_api_get_multiple_response(
        self,
        objs: List[Permission],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> PermissionMultipleResponse:
        return PermissionMultipleResponse(
            pagination=PaginationInfo(
                offset=query_offset, limit=query_limit, total_count=total_count
            ),
            permissions=[
                ResponsePermission(
                    name=ManagementObjectName(permission.name),
                    display_name=permission.display_name,
                    app_name=ManagementObjectName(permission.app_name),
                    namespace_name=ManagementObjectName(permission.namespace_name),
                    resource_url=f"{COMPLETE_URL}/permissions/{permission.app_name}/"
                    f"{permission.namespace_name}/{permission.name}",
                )
                for permission in objs
            ],
        )


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
            app_name=db_app.name,
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
        result = await self._get_single_object(
            DBPermission,
            name=query.name,
            app_name=query.app_name,
            namespace_name=query.namespace_name,
        )
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
        dp_permissions, total_count = await self._get_many_objects(
            DBPermission,
            query.pagination.query_offset,
            query.pagination.query_limit,
            app_name=query.app_name,
            namespace_name=query.namespace_name,
        )
        permissions = [
            SQLPermissionPersistenceAdapter._db_permission_to_permission(db_permission)
            for db_permission in dp_permissions
        ]
        return PersistenceGetManyResult(total_count=total_count, objects=permissions)

    async def update(self, permission: Permission) -> Permission:
        db_permission = await self._get_single_object(
            DBPermission,
            name=permission.name,
            app_name=permission.app_name,
            namespace_name=permission.namespace_name,
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
