# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import os
from typing import Optional
from urllib.parse import urljoin

from ..models.app import App, AppCreateQuery, AppGetQuery, Apps
from ..models.role import ResponseRole
from ..models.routes import (
    AppAdminResponse,
    ManagementAppCreateRequest,
    ManagementAppCreateResponse,
    ManagementAppGetRequest,
    ManagementAppGetResponse,
)
from ..ports.app import (
    AppAPIPort,
    AppPersistencePort,
)

API_PREFIX = os.environ.get("GUARDIAN__MANAGEMENT__API_PREFIX", "/guardian/management")
BASE_URL = os.environ.get("GUARDIAN__MANAGEMENT__BASE_URL", "https://localhost/")
COMPLETE_URL = urljoin(BASE_URL, API_PREFIX)


class FastAPIAppAPIAdapter(
    AppAPIPort[
        ManagementAppCreateRequest,
        ManagementAppCreateResponse,
        ManagementAppGetRequest,
        ManagementAppGetResponse,
    ]
):
    class Config:
        alias = "fastapi"

    async def to_app_create(
        self, api_request: ManagementAppCreateRequest
    ) -> AppCreateQuery:
        return AppCreateQuery(
            apps=[
                App(
                    name=api_request.name.__root__,
                    display_name=api_request.display_name,
                )
            ]
        )

    async def to_api_create_response(
        self, app_result: App
    ) -> ManagementAppCreateResponse:
        return ManagementAppCreateResponse(
            name=app_result.name,
            display_name=app_result.display_name,
            resource_url=f"{COMPLETE_URL}/apps/{app_result.name}",
            app_admin=AppAdminResponse(
                name=f"{app_result.name}-admin",
                display_name=f"{app_result.name} Admin",
                role=ResponseRole(
                    namespace_name=app_result.name,
                    name="app-admin",
                    app_name="guardian",
                    resource_url=f"{COMPLETE_URL}/roles/{app_result.name}/app-admin",
                    display_name=f"{app_result.name} App Admin",
                ),
            ),
        )

    async def to_app_get(self, api_request: ManagementAppGetRequest) -> AppGetQuery:
        return AppGetQuery(apps=[App(name=api_request.name, display_name="")])

    async def to_api_get_response(
        self, app_result: App | None
    ) -> ManagementAppGetResponse | None:
        if not app_result:
            return None
        return ManagementAppGetResponse(
            name=app_result.name,
            display_name=app_result.display_name,
            resource_url=f"{COMPLETE_URL}/apps/{app_result.name}",
            app_admin=AppAdminResponse(
                name=f"{app_result.name}-admin",
                display_name=f"{app_result.name} Admin",
                role=ResponseRole(
                    namespace_name=app_result.name,
                    name="app-admin",
                    app_name="guardian",
                    resource_url=f"{COMPLETE_URL}/roles/{app_result.name}/app-admin",
                    display_name=f"{app_result.name} App Admin",
                ),
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
        raise NotImplementedError  # pragma: no cover

    async def update(
        self,
        app: App,
    ) -> App:
        # self._data.apps = [
        #    app if app.name == app.name else app for app in self._data.apps
        # ]
        # return app
        raise NotImplementedError  # pragma: no cover
