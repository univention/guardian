# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import asdict
from typing import Any, List, Optional, Tuple, Type

from port_loader import AsyncConfiguredAdapterMixin

from ..constants import COMPLETE_URL
from ..errors import ObjectNotFoundError
from ..models.app import (
    App,
    AppCreateQuery,
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
from .fastapi_utils import TransformExceptionMixin
from .sql_persistence import SQLAlchemyMixin


class TransformAppExceptionMixin(TransformExceptionMixin):
    ...


class FastAPIAppAPIAdapter(
    TransformAppExceptionMixin,
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
    ],
):
    class Config:
        alias = "fastapi"

    async def to_app_create(self, api_request: AppCreateRequest) -> AppCreateQuery:
        return AppCreateQuery(
            apps=[
                App(
                    name=api_request.name,
                    display_name=api_request.display_name,
                )
            ]
        )

    async def to_app_edit(
        self, api_request: AppEditRequest
    ) -> Tuple[AppGetQuery, dict[str, Any]]:
        query = AppGetQuery(name=api_request.name)
        changed_data = api_request.data.dict(exclude_unset=True)
        return query, changed_data

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
                f"No app with the identifier '{query.name} could be found."
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
