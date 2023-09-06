# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Type

from fastapi import HTTPException
from port_loader import AsyncConfiguredAdapterMixin
from starlette import status

from ..constants import COMPLETE_URL
from ..errors import ObjectExistsError, ObjectNotFoundError
from ..models.app import (
    App,
    AppCreateQuery,
    AppEditQuery,
    AppGetQuery,
    AppsGetQuery,
)
from ..models.base import PaginationRequest, PersistenceGetManyResult
from ..models.namespace import Namespace
from ..models.role import Role
from ..models.routers.app import (
    App as ResponseApp,
)
from ..models.routers.app import (
    AppAdmin,
    AppCreateRequest,
    AppDefaultNamespace,
    AppEditRequest,
    AppGetRequest,
    AppMultipleResponse,
    AppRegisterResponse,
    AppsGetRequest,
    AppSingleResponse,
)
from ..models.routers.base import ManagementObjectName, PaginationInfo
from ..models.sql_persistence import DBApp, SQLPersistenceAdapterSettings
from ..ports.app import (
    AppAPIPort,
    AppPersistencePort,
)
from .sql_persistence import SQLAlchemyMixin


class FastAPIAppAPIAdapter(
    AppAPIPort[
        AppCreateRequest,
        AppSingleResponse,
        AppRegisterResponse,
        AppGetRequest,
        AppSingleResponse,
        AppsGetRequest,
        AppMultipleResponse,
        AppEditRequest,
        AppSingleResponse,
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
        if isinstance(exc, ObjectExistsError):
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "App with the same name already exists."},
            )
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal Server Error"},
        )

    async def to_app_create(self, api_request: AppCreateRequest) -> AppCreateQuery:
        return AppCreateQuery(
            apps=[
                App(
                    name=api_request.name,
                    display_name=api_request.display_name,
                )
            ]
        )

    async def to_app_edit(self, api_request: AppEditRequest) -> AppEditQuery:
        return AppEditQuery(
            apps=[
                App(
                    name=api_request.name,
                    display_name=api_request.data.display_name,
                )
            ]
        )

    async def to_api_edit_response(self, app_result: App) -> AppSingleResponse:
        return AppSingleResponse(
            app=ResponseApp(
                name=ManagementObjectName(app_result.name),
                display_name=app_result.display_name,
                resource_url=f"{COMPLETE_URL}/apps/{app_result.name}",
            )
        )

    async def to_api_create_response(self, app_result: App) -> AppSingleResponse:
        return AppSingleResponse(
            app=ResponseApp(
                name=ManagementObjectName(app_result.name),
                display_name=app_result.display_name,
                resource_url=f"{COMPLETE_URL}/apps/{app_result.name}",
            )
        )

    async def to_api_register_response(
        self, app: App, default_namespace: Namespace, admin_role: Role
    ) -> AppRegisterResponse:
        return AppRegisterResponse(
            app=ResponseApp(
                name=ManagementObjectName(app.name),
                display_name=app.display_name,
                resource_url=f"{COMPLETE_URL}/guardian/management/apps/{app.name}",
            ),
            admin_role=AppAdmin(
                app_name=ManagementObjectName(admin_role.app_name),
                namespace_name=ManagementObjectName(admin_role.namespace_name),
                name=ManagementObjectName(admin_role.name),
                display_name=admin_role.display_name,
                resource_url=f"{COMPLETE_URL}/roles/{admin_role.app_name}/{admin_role.namespace_name}/{admin_role.name}",
            ),
            default_namespace=AppDefaultNamespace(
                app_name=ManagementObjectName(default_namespace.app_name),
                name=ManagementObjectName(default_namespace.name),
                display_name=default_namespace.display_name,
                resource_url=f"{COMPLETE_URL}/namespaces/{default_namespace.app_name}/{default_namespace.name}",
            ),
        )

    async def to_app_get(self, api_request: AppGetRequest) -> AppGetQuery:
        return AppGetQuery(name=api_request.name)

    async def to_api_get_response(self, app_result: App) -> AppSingleResponse:
        return AppSingleResponse(
            app=ResponseApp(
                name=ManagementObjectName(app_result.name),
                display_name=app_result.display_name,
                resource_url=f"{COMPLETE_URL}/apps/{app_result.name}",
            )
        )

    async def to_apps_get(self, api_request: AppsGetRequest) -> AppsGetQuery:
        return AppsGetQuery(
            pagination=PaginationRequest(
                query_offset=api_request.offset,
                query_limit=api_request.limit,
            )
        )

    async def to_api_apps_get_response(
        self,
        apps: List[App],
        query_offset: int,
        query_limit: Optional[int],
        total_count: int,
    ) -> AppMultipleResponse:
        return AppMultipleResponse(
            pagination=PaginationInfo(
                offset=query_offset,
                limit=query_limit,
                total_count=total_count,
            ),
            apps=[
                ResponseApp(
                    name=ManagementObjectName(app.name),
                    display_name=app.display_name,
                    resource_url=f"{COMPLETE_URL}/apps/{app.name}",
                )
                for app in apps
            ],
        )


class AppStaticDataAdapter(AppPersistencePort):
    class Config:
        alias = "in_memory"

    _data: Dict[str, Any] = {
        "apps": [],
    }

    async def create(
        self,
        app: App,
    ) -> App:
        self._data["apps"].append(app)
        return app

    async def read_one(
        self,
        query: AppGetQuery,
    ) -> App:
        result = next(
            (app for app in self._data["apps"] if app.name == query.name), None
        )
        if result is None:
            raise ObjectNotFoundError(
                f"No permission with the identifier '{query.name} could be found"
            )
        return result

    async def read_many(
        self,
        query: AppsGetQuery,
    ) -> PersistenceGetManyResult[App]:
        total_count = len(self._data["apps"])
        result = []

        if query.pagination.query_limit:
            result = self._data["apps"][
                query.pagination.query_offset : query.pagination.query_offset
                + query.pagination.query_limit
            ]
        else:
            result = self._data["apps"][query.pagination.query_offset :]

        return PersistenceGetManyResult(objects=result, total_count=total_count)

    async def update(
        self,
        updated_app: App,
    ) -> App:  # pragma: no cover  static data adapter is deprecated
        if not any(app.name == updated_app.name for app in self._data["apps"]):
            raise ObjectNotFoundError("The app could not be found.")
        self._data["apps"] = [
            updated_app if app.name == updated_app.name else app
            for app in self._data["apps"]
        ]
        return updated_app


class SQLAppPersistenceAdapter(
    AsyncConfiguredAdapterMixin, AppPersistencePort, SQLAlchemyMixin
):
    @staticmethod
    def _app_to_db_app(app: App) -> DBApp:
        return DBApp(name=app.name, display_name=app.display_name)

    @staticmethod
    def _db_app_to_app(db_app: DBApp) -> App:
        return App(name=db_app.name, display_name=db_app.display_name)

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

    async def create(self, app: App) -> App:
        db_app = SQLAppPersistenceAdapter._app_to_db_app(app)
        result = await self._create_object(db_app)
        return SQLAppPersistenceAdapter._db_app_to_app(result)

    async def read_one(self, query: AppGetQuery) -> App:
        result = await self._get_single_object(DBApp, name=query.name)
        if result is None:
            raise ObjectNotFoundError(
                f"No permission with the identifier '{query.name} could be found."
            )
        return SQLAppPersistenceAdapter._db_app_to_app(result)

    async def read_many(
        self,
        query: AppsGetQuery,
    ) -> PersistenceGetManyResult[App]:
        db_apps, total_count = await self._get_many_objects(
            DBApp, query.pagination.query_offset, query.pagination.query_limit
        )
        apps = [SQLAppPersistenceAdapter._db_app_to_app(db_app) for db_app in db_apps]
        return PersistenceGetManyResult(total_count=total_count, objects=apps)

    async def update(self, app: App) -> App:
        db_app = await self._get_single_object(DBApp, name=app.name)
        if db_app is None:
            raise ObjectNotFoundError(
                f"No app with the name '{app.name}' could be found."
            )
        modified = await self._update_object(db_app, display_name=app.display_name)
        return SQLAppPersistenceAdapter._db_app_to_app(modified)
