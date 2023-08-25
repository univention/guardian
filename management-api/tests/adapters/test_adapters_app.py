# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
from guardian_management_api.adapters.app import (
    AppStaticDataAdapter,
    FastAPIAppAPIAdapter,
)
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.models.app import (
    App,
    AppCreateQuery,
    AppGetQuery,
    AppsGetQuery,
)
from guardian_management_api.models.base import (
    PaginationRequest,
    PersistenceGetManyResult,
)
from guardian_management_api.models.routers.app import (
    App as ResponseApp,
)
from guardian_management_api.models.routers.app import (
    AppAdmin,
    AppCreateRequest,
    AppGetRequest,
    AppSingleResponse,
)
from guardian_management_api.models.routers.role import Role as ResponseRole


class TestFastAPIAppAdapter:
    @pytest.fixture(autouse=True)
    def adapter(self):
        return FastAPIAppAPIAdapter()

    @pytest.mark.asyncio
    async def test_to_app_create(self, adapter):
        api_request = AppCreateRequest(
            name="name",
            display_name="display_name",
        )
        result = await adapter.to_app_create(api_request)
        assert result == AppCreateQuery(
            apps=[
                App(
                    name="name",
                    display_name="display_name",
                )
            ],
        )

    @pytest.mark.asyncio
    async def test_to_api_create_response(self, adapter):
        app = App(
            name="name",
            display_name="display_name",
        )
        result = await adapter.to_api_create_response(app)
        assert result == AppSingleResponse(
            app=ResponseApp(
                name="name",
                display_name="display_name",
                resource_url=f"{COMPLETE_URL}/apps/name",
                app_admin=AppAdmin(
                    name="name-admin",
                    display_name="name Admin",
                    role=ResponseRole(
                        resource_url=f"{COMPLETE_URL}/roles/name/app-admin",
                        app_name="guardian",
                        namespace_name="name",
                        name="app-admin",
                        display_name="name App Admin",
                    ),
                ),
            )
        )

    @pytest.mark.asyncio
    async def test_to_app_get(self, adapter):
        api_request = AppGetRequest(
            name="name",
        )
        result = await adapter.to_app_get(api_request)
        assert result == AppGetQuery(name="name")

    @pytest.mark.asyncio
    async def test_to_api_get_response(self, adapter):
        app = App(
            name="name",
            display_name="display_name",
        )
        result = await adapter.to_api_get_response(app)
        assert result == AppSingleResponse(
            app=ResponseApp(
                name="name",
                display_name="display_name",
                resource_url=f"{COMPLETE_URL}/apps/name",
                app_admin=AppAdmin(
                    name="name-admin",
                    display_name="name Admin",
                    role=ResponseRole(
                        resource_url=f"{COMPLETE_URL}/roles/name/app-admin",
                        app_name="guardian",
                        namespace_name="name",
                        name="app-admin",
                        display_name="name App Admin",
                    ),
                ),
            )
        )


class TestAppStaticDataAdapter:
    @pytest.fixture(autouse=True)
    def adapter(self):
        return AppStaticDataAdapter()

    @pytest.mark.asyncio
    async def test_create(self, adapter):
        app = App(
            name="name",
            display_name="display_name",
        )
        result = await adapter.create(app)
        assert result == app
        assert app in adapter._data["apps"]

    @pytest.mark.asyncio
    async def test_read_one(self, adapter):
        app = App(
            name="name",
            display_name="display_name",
        )
        adapter._data["apps"].append(app)
        result = await adapter.read_one(query=AppGetQuery(name=app.name))
        assert result == app

    apps = [
        App(
            name="name",
            display_name="display_name",
        ),
        App(
            name="name2",
            display_name="display_name2",
        ),
    ]

    @pytest.mark.parametrize(
        "query,expected",
        [
            (
                AppsGetQuery(
                    pagination=PaginationRequest(query_offset=0, query_limit=None),
                ),
                PersistenceGetManyResult(objects=apps, total_count=2),
            ),
            (
                AppsGetQuery(
                    pagination=PaginationRequest(
                        query_offset=0,
                        query_limit=1,
                    ),
                ),
                PersistenceGetManyResult(objects=apps[:1], total_count=2),
            ),
            (
                AppsGetQuery(
                    pagination=PaginationRequest(
                        query_offset=1,
                        query_limit=10,
                    )
                ),
                PersistenceGetManyResult(objects=apps[1:], total_count=2),
            ),
            (
                AppsGetQuery(
                    pagination=PaginationRequest(
                        query_offset=1,
                        query_limit=1,
                    )
                ),
                PersistenceGetManyResult(objects=apps[1:2], total_count=2),
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_read_many(self, adapter, query, expected):
        adapter._data["apps"] = self.apps
        result = await adapter.read_many(query)
        assert result == expected
