# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Optional

from ..constants import COMPLETE_URL
from ..models.app import App, AppCreateQuery, AppGetQuery, Apps
from ..models.role import ResponseRole
from ..models.routers.app import (
    AppAdminResponse,
    AppCreateRequest,
    AppCreateResponse,
    AppGetRequest,
    AppGetResponse,
)
from ..ports.app import (
    AppAPIPort,
    AppPersistencePort,
)


class FastAPIAppAPIAdapter(
    AppAPIPort[
        AppCreateRequest,
        AppCreateResponse,
        AppGetRequest,
        AppGetResponse,
    ]
):
    class Config:
        alias = "fastapi"

    async def to_app_create(self, api_request: AppCreateRequest) -> AppCreateQuery:
        return AppCreateQuery(
            apps=[
                App(
                    name=api_request.name.__root__,
                    display_name=api_request.display_name,
                )
            ]
        )

    async def to_api_create_response(self, app_result: App) -> AppCreateResponse:
        return AppCreateResponse(
            name=app_result.name,
            display_name=app_result.display_name,
            resource_url=f"{COMPLETE_URL}/apps/{app_result.name}",
            # TODO: this is currently hardcoded, should be fixed in the future
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

    async def to_app_get(self, api_request: AppGetRequest) -> AppGetQuery:
        return AppGetQuery(apps=[App(name=api_request.name, display_name="")])

    async def to_api_get_response(
        self, app_result: App | None
    ) -> AppGetResponse | None:
        if not app_result:
            return None
        return AppGetResponse(
            name=app_result.name,
            display_name=app_result.display_name,
            resource_url=f"{COMPLETE_URL}/apps/{app_result.name}",
            # TODO: this is currently hardcoded, should be fixed in the future
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
