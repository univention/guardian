# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from typing import cast

import pytest
import pytest_asyncio
from fastapi import HTTPException
from guardian_management_api.adapters.app import (
    FastAPIAppAPIAdapter,
    SQLAppPersistenceAdapter,
)
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.errors import (
    ObjectExistsError,
    ObjectNotFoundError,
    PersistenceError,
    UnauthorizedError,
)
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
from guardian_management_api.models.namespace import Namespace
from guardian_management_api.models.role import Role
from guardian_management_api.models.routers.app import (
    App as ResponseApp,
)
from guardian_management_api.models.routers.app import (
    AppAdmin,
    AppCreateRequest,
    AppDefaultNamespace,
    AppEditData,
    AppEditRequest,
    AppGetRequest,
    AppRegisterResponse,
    AppSingleResponse,
)
from guardian_management_api.models.routers.base import ManagementObjectName
from guardian_management_api.models.sql_persistence import (
    DBApp,
)
from guardian_management_api.ports.app import AppPersistencePort
from sqlalchemy import select


class TestFastAPIAppAdapter:
    @pytest.fixture(autouse=True)
    def adapter(self):
        return FastAPIAppAPIAdapter()

    @pytest.mark.parametrize(
        "exc,expected",
        [
            (ObjectNotFoundError(), 404),
            (PersistenceError(), 500),
            (ValueError, 500),
            (ObjectExistsError(), 400),
            (UnauthorizedError(), 403),
        ],
    )
    @pytest.mark.asyncio
    async def test_transform_exception(self, exc, expected, adapter):
        result: HTTPException = cast(
            HTTPException, await adapter.transform_exception(exc)
        )
        assert result.status_code == expected

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
            )
        )

    @pytest.mark.asyncio
    async def test_to_api_register_response(self, adapter):
        app = App(name="app", display_name="App")
        default_namespace = Namespace(
            app_name="app", name="default", display_name="Default Namespace for App"
        )
        admin_role = Role(
            app_name="app",
            namespace_name="default",
            name="admin-role",
            display_name="App Administrator for App",
        )
        assert await adapter.to_api_register_response(
            app, default_namespace, admin_role
        ) == AppRegisterResponse(
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
            )
        )

    @pytest.mark.asyncio
    async def test_to_api_edit_response(self, adapter):
        app = App(
            name="name",
            display_name="display_name",
        )
        result = await adapter.to_api_edit_response(app)
        assert result == AppSingleResponse(
            app=ResponseApp(
                name="name",
                display_name="display_name",
                resource_url=f"{COMPLETE_URL}/apps/name",
            )
        )

    @pytest.mark.asyncio
    async def test_to_app_edit(self, adapter):
        api_request = AppEditRequest(
            name="name",
            data=AppEditData(
                display_name="display_name",
            ),
        )
        query, changed_data = await adapter.to_app_edit(api_request)
        assert query == AppGetQuery(name="name")
        assert changed_data == {"display_name": "display_name"}


class TestSQLAppPersistenceAdapter:
    @pytest_asyncio.fixture
    async def app_sql_adapter(self, registry_test_adapters) -> SQLAppPersistenceAdapter:
        return await registry_test_adapters.request_port(AppPersistencePort)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create(self, app_sql_adapter: SQLAppPersistenceAdapter):
        app = await app_sql_adapter.create(App(name="app", display_name="App"))
        assert app == App(name="app", display_name="App")
        async with app_sql_adapter.session() as session:
            result = (await session.scalars(select(DBApp))).one()
            assert result.name == "app"
            assert result.display_name == "App"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_exists_error(
        self, app_sql_adapter: SQLAppPersistenceAdapter, create_app
    ):
        async with app_sql_adapter.session() as session:
            app = await create_app(session)
        with pytest.raises(ObjectExistsError):
            await app_sql_adapter.create(App(name=app.name, display_name="App"))

    @pytest.mark.asyncio
    async def test_create_unhandled_error(
        self, app_sql_adapter: SQLAppPersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await app_sql_adapter.create(App(name="app", display_name="App"))

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one(
        self, app_sql_adapter: SQLAppPersistenceAdapter, create_app
    ):
        async with app_sql_adapter.session() as session:
            db_app = await create_app(session)
        app = await app_sql_adapter.read_one(AppGetQuery(name=db_app.name))
        assert app.name == db_app.name
        assert app.display_name == db_app.display_name

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one_none(
        self, app_sql_adapter: SQLAppPersistenceAdapter, create_app
    ):
        async with app_sql_adapter.session() as session:
            await create_app(session)
        with pytest.raises(ObjectNotFoundError):
            await app_sql_adapter.read_one(AppGetQuery(name="other_app"))

    @pytest.mark.asyncio
    async def test_read_one_unhandled_error(
        self, app_sql_adapter: SQLAppPersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await app_sql_adapter.read_one(AppGetQuery(name="other_app"))

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update(self, app_sql_adapter: SQLAppPersistenceAdapter, create_app):
        async with app_sql_adapter.session() as session:
            db_app = await create_app(session)
        result = await app_sql_adapter.update(
            App(name=db_app.name, display_name="NEW DISPLAY NAME")
        )
        assert result == App(name=db_app.name, display_name="NEW DISPLAY NAME")
        async with app_sql_adapter.session() as session:
            result = (await session.scalars(select(DBApp))).one()
            assert result.name == result.name
            assert result.display_name == result.display_name

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update_object_not_found_error(
        self, app_sql_adapter: SQLAppPersistenceAdapter, create_app
    ):
        async with app_sql_adapter.session() as session:
            await create_app(session)
        with pytest.raises(
            ObjectNotFoundError, match="No app with the name 'some_app' could be found."
        ):
            await app_sql_adapter.update(
                App(name="some_app", display_name="NEW DISPLAY NAME")
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_many_empty(self, app_sql_adapter: SQLAppPersistenceAdapter):
        result = await app_sql_adapter.read_many(
            AppsGetQuery(pagination=PaginationRequest(query_offset=0))
        )
        assert result == PersistenceGetManyResult(total_count=0, objects=[])

    @pytest.mark.asyncio
    async def test_read_many_unhandled_error(
        self, app_sql_adapter: SQLAppPersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await app_sql_adapter.read_many(
                AppsGetQuery(pagination=PaginationRequest(query_offset=0))
            )

    @pytest.mark.parametrize(
        "limit,offset",
        [
            (5, 0),
            (None, 0),
            (5, 5),
            (None, 20),
            (1000, 0),
            (1000, 5),
            (None, 1000),
            (5, 1000),
            (0, 5),
            (0, 0),
        ],
    )
    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_many_limit_offset(
        self, app_sql_adapter: SQLAppPersistenceAdapter, create_apps, limit, offset
    ):
        async with app_sql_adapter.session() as session:
            apps = await create_apps(session, num_apps=100)
        result = await app_sql_adapter.read_many(
            AppsGetQuery(
                pagination=PaginationRequest(query_offset=offset, query_limit=limit)
            )
        )
        selected_slice = apps[offset : offset + limit] if limit else apps[offset:]
        assert result.total_count == 100
        assert [obj.name for obj in result.objects] == [
            obj.name for obj in selected_slice
        ]
