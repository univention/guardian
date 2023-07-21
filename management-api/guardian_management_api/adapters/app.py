# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Optional

from ..models.app import App, AppCreateQuery, AppGetQuery, Apps
from ..models.routes import (
    ManagementAppCreateRequest,
    ManagementAppCreateResponse,
    ManagementAppGetRequest,
    ManagementAppGetResponse,
    RoleResponse,
)
from ..ports.app import (
    AppAPIPort,
    AppPersistencePort,
)


class FastAPIAppAPIAdapter(
    AppAPIPort[
        ManagementAppCreateRequest,
        ManagementAppCreateResponse,
        ManagementAppGetRequest,
        ManagementAppGetResponse,
    ]
):
    async def create_to_query(
        self, api_request: ManagementAppCreateRequest
    ) -> AppCreateQuery:
        return AppCreateQuery(
            apps=[App(name=api_request.name, display_name=api_request.display_name)]
        )

    async def create_to_api_response(
        self, app_result: App
    ) -> ManagementAppCreateResponse:
        return ManagementAppCreateResponse(
            name=app_result.name,
            display_name=app_result.display_name,
            resource_url="",
            app_admin=RoleResponse(
                namespace="default", name="admin", display_name="admin"
            ),
        )

    async def get_to_query(self, api_request: ManagementAppGetRequest) -> AppGetQuery:
        return AppGetQuery(apps=[App(name=api_request.name, display_name="")])

    async def get_to_api_response(
        self, app_result: App | None
    ) -> ManagementAppGetResponse | None:
        if not app_result:
            return None
        return ManagementAppGetResponse(
            name=app_result.name,
            display_name=app_result.display_name,
            resource_url="",
            app_admin=RoleResponse(
                namespace="default", name="admin", display_name="admin"
            ),
        )


class AppStaticDataAdapter(AppPersistencePort):
    class Config:
        alias = "in_memory"

    _data: Apps = Apps()

    async def create(
        self,
        app: App,
    ) -> App:
        self._data.apps.append(app)
        return app

    async def read_one(
        self,
        query: AppGetQuery,
    ) -> App | None:
        return next(
            (app for app in self._data.apps if app.name == query.apps[0].name), None
        )

    async def read_many(
        self,
        query_offset: Optional[int] = None,
        query_limit: Optional[int] = None,
    ) -> Apps:
        return Apps(apps=self._data.apps[query_offset:query_limit])

    async def update(
        self,
        app: App,
    ) -> App:
        self._data.apps = [
            app if app.name == app.name else app for app in self._data.apps
        ]
        return app
