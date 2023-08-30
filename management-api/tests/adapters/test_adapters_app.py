# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
import pytest_asyncio
from guardian_management_api.adapters.app import (
    AppStaticDataAdapter,
    FastAPIAppAPIAdapter,
    SQLAppPersistenceAdapter,
)
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.errors import (
    ObjectExistsError,
    ObjectNotFoundError,
    PersistenceError,
)
from guardian_management_api.models.app import (
    App,
    AppCreateQuery,
    AppEditQuery,
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
    AppEditData,
    AppEditRequest,
    AppGetRequest,
    AppSingleResponse,
)
from guardian_management_api.models.routers.role import Role as ResponseRole
from guardian_management_api.models.sql_persistence import (
    DBApp,
    SQLPersistenceAdapterSettings,
)
from sqlalchemy import select


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
    async def test_to_app_edit(self, adapter):
        api_request = AppEditRequest(
            name="name",
            data=AppEditData(
                display_name="display_name",
            ),
        )
        result = await adapter.to_app_edit(api_request)
        assert result == AppEditQuery(
            apps=[
                App(
                    name="name",
                    display_name="display_name",
                )
            ],
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


class TestSQLAppPersistenceAdapter:
    @pytest_asyncio.fixture
    async def app_sql_adapter(self, sqlite_url) -> SQLAppPersistenceAdapter:
        adapter = SQLAppPersistenceAdapter()
        await adapter.configure(
            SQLPersistenceAdapterSettings(dialect="sqlite", db_name=sqlite_url)
        )
        return adapter

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
        app = await app_sql_adapter.read_one(AppGetQuery(name="other_app"))
        assert app is None

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
