import pytest
from guardian_management_api.adapters.app import (
    AppStaticDataAdapter,
    FastAPIAppAPIAdapter,
)
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.models.app import App, AppCreateQuery, AppGetQuery
from guardian_management_api.models.role import ResponseRole
from guardian_management_api.models.routers.app import (
    AppAdminResponse,
    AppCreateRequest,
    AppCreateResponse,
    AppGetRequest,
    AppGetResponse,
)


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
        assert result == AppCreateResponse(
            name="name",
            display_name="display_name",
            resource_url=f"{COMPLETE_URL}/apps/name",
            app_admin=AppAdminResponse(
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

    @pytest.mark.asyncio
    async def test_to_app_get(self, adapter):
        api_request = AppGetRequest(
            name="name",
        )
        result = await adapter.to_app_get(api_request)
        assert result == AppGetQuery(
            apps=[App(name="name", display_name="")],
        )

    @pytest.mark.asyncio
    async def test_to_api_get_response(self, adapter):
        app = App(
            name="name",
            display_name="display_name",
        )
        result = await adapter.to_api_get_response(app)
        assert result == AppGetResponse(
            name="name",
            display_name="display_name",
            resource_url=f"{COMPLETE_URL}/apps/name",
            app_admin=AppAdminResponse(
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
        assert app in adapter._data.apps

    @pytest.mark.asyncio
    async def test_read_one(self, adapter):
        app = App(
            name="name",
            display_name="display_name",
        )
        adapter._data.apps.append(app)
        result = await adapter.read_one(query=AppGetQuery(apps=[app]))
        assert result == app
