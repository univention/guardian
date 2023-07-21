# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


import pytest
from guardian_management_api.models.app import App, AppCreateQuery, AppGetQuery, Apps
from guardian_management_api.ports.app import (
    AppAPICreateRequestObject,
    AppAPICreateResponseObject,
    AppAPIGetRequestObject,
    AppAPIGetResponseObject,
    AppAPIPort,
    AppPersistencePort,
)


class AppAPIPortAdapter(AppAPIPort):
    async def create_to_query(
        self, api_request: AppAPICreateRequestObject
    ) -> AppCreateQuery:
        pass

    async def create_to_api_response(
        self, app_result: App
    ) -> AppAPICreateResponseObject:
        pass

    async def get_to_query(self, api_request: AppAPIGetRequestObject) -> AppGetQuery:
        pass

    async def get_to_api_response(
        self, app_result: App | None
    ) -> AppAPIGetResponseObject | None:
        pass


class TestAppAPIPort:
    @pytest.mark.asyncio
    async def test_app_api_port(self):
        adapter = AppAPIPortAdapter()
        assert isinstance(adapter, AppAPIPort)
        await adapter.create_to_query(api_request=None)
        await adapter.create_to_api_response(app_result=None)
        await adapter.get_to_query(api_request=None)
        await adapter.get_to_api_response(app_result=None)


class AppPersistencePortAdapter(AppPersistencePort):
    async def create(self, query: AppCreateQuery) -> App:
        pass

    async def read_one(self, query: AppGetQuery) -> App | None:
        pass

    async def read_many(self, query: AppGetQuery) -> Apps:
        pass

    async def update(self, query: AppCreateQuery) -> App:
        pass


class TestAppPersistencePort:
    @pytest.mark.asyncio
    async def test_app_persistence_port(self):
        adapter = AppPersistencePortAdapter()
        assert isinstance(adapter, AppPersistencePort)
        await adapter.create(query=None)
        await adapter.read_one(query=None)
        await adapter.read_many(query=None)
        await adapter.update(query=None)
