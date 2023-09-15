# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
import pytest_asyncio
from guardian_management_api.adapters.namespace import (
    FastAPINamespaceAPIAdapter,
    SQLNamespacePersistenceAdapter,
)
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.errors import (
    ObjectExistsError,
    ObjectNotFoundError,
    ParentNotFoundError,
    PersistenceError,
)
from guardian_management_api.models.base import (
    PaginationRequest,
    PersistenceGetManyResult,
)
from guardian_management_api.models.namespace import (
    Namespace,
    NamespaceCreateQuery,
    NamespaceEditQuery,
    NamespaceGetQuery,
    NamespacesGetQuery,
)
from guardian_management_api.models.routers.base import PaginationInfo
from guardian_management_api.models.routers.namespace import (
    Namespace as ResponseNamespace,
)
from guardian_management_api.models.routers.namespace import (
    NamespaceCreateData,
    NamespaceCreateRequest,
    NamespaceEditData,
    NamespaceEditRequest,
    NamespaceGetRequest,
    NamespaceMultipleResponse,
    NamespacesByAppnameGetRequest,
    NamespacesGetRequest,
    NamespaceSingleResponse,
)
from guardian_management_api.models.sql_persistence import (
    DBNamespace,
)
from guardian_management_api.ports.namespace import NamespacePersistencePort
from sqlalchemy import select


class TestFastAPINamespaceAdapter:
    @pytest.fixture(autouse=True)
    def adapter(self):
        return FastAPINamespaceAPIAdapter()

    @pytest.mark.asyncio
    async def test_to_namespace_create(self, adapter):
        app_name = "app-name"
        api_request = NamespaceCreateRequest(
            app_name=app_name,
            data=NamespaceCreateData(
                display_name="display_name", name="namespace-name"
            ),
        )
        result = await adapter.to_namespace_create(api_request)
        assert result == NamespaceCreateQuery(
            name="namespace-name",
            display_name="display_name",
            app_name=app_name,
        )

    @pytest.mark.asyncio
    async def test_to_api_create_response(self, adapter):
        namespace = Namespace(
            name="name", display_name="display_name", app_name="app-name"
        )
        result = await adapter.to_api_create_response(namespace)
        assert result == NamespaceSingleResponse(
            namespace=ResponseNamespace(
                name=namespace.name,
                app_name=namespace.app_name,
                display_name=namespace.display_name,
                resource_url=f"{COMPLETE_URL}/namespaces/{namespace.app_name}/{namespace.name}",
            )
        )

    @pytest.mark.asyncio
    async def test_to_namespace_get(self, adapter):
        app_name = "app-name"
        api_request = NamespaceGetRequest(
            app_name=app_name,
            name="namespace-name",
        )
        result = await adapter.to_namespace_get(api_request)
        assert result == NamespaceGetQuery(
            name="namespace-name",
            app_name=app_name,
        )

    @pytest.mark.asyncio
    async def test_to_api_get_response(self, adapter):
        namespace = Namespace(
            name="name", display_name="display_name", app_name="app-name"
        )
        result = await adapter.to_api_get_response(namespace)
        assert result == NamespaceSingleResponse(
            namespace=ResponseNamespace(
                name=namespace.name,
                app_name=namespace.app_name,
                display_name=namespace.display_name,
                resource_url=f"{COMPLETE_URL}/namespaces/{namespace.app_name}/{namespace.name}",
            )
        )

    @pytest.mark.asyncio
    async def test_to_namespaces_get(self, adapter):
        api_request = NamespacesGetRequest(offset=0, limit=1)
        result = await adapter.to_namespaces_get(api_request)
        assert result == NamespacesGetQuery(
            pagination=PaginationRequest(query_offset=0, query_limit=1)
        )

    @pytest.mark.asyncio
    async def test_to_api_namespaces_get_response(self, adapter):
        namespaces = [
            Namespace(
                name=f"name-{i}", display_name="display_name", app_name="app-name"
            )
            for i in range(3)
        ]
        result = await adapter.to_api_namespaces_get_response(
            list(namespaces), query_offset=0, query_limit=3, total_count=len(namespaces)
        )
        expected_namespaces = [
            ResponseNamespace(
                name=namespace.name,
                app_name=namespace.app_name,
                display_name=namespace.display_name,
                resource_url=f"{COMPLETE_URL}/namespaces/{namespace.app_name}/{namespace.name}",
            )
            for namespace in namespaces
        ]
        assert result == NamespaceMultipleResponse(
            namespaces=list(expected_namespaces),
            pagination=PaginationInfo(
                offset=0,
                limit=3,
                total_count=len(namespaces),
            ),
        )

    @pytest.mark.asyncio
    async def test_to_api_edit_response(self, adapter):
        namespace = Namespace(
            name="name", display_name="display_name", app_name="app-name"
        )
        result = await adapter.to_api_edit_response(namespace)
        assert result == NamespaceSingleResponse(
            namespace=ResponseNamespace(
                name=namespace.name,
                app_name=namespace.app_name,
                display_name=namespace.display_name,
                resource_url=f"{COMPLETE_URL}/namespaces/{namespace.app_name}/{namespace.name}",
            )
        )

    @pytest.mark.asyncio
    async def test_to_namespaces_by_appname_get(self, adapter):
        api_request = NamespacesByAppnameGetRequest(
            offset=0, limit=1, app_name="test-app"
        )
        result = await adapter.to_namespaces_by_appname_get(api_request)
        assert result == NamespacesGetQuery(
            pagination=PaginationRequest(query_offset=0, query_limit=1),
            app_name="test-app",
        )

    @pytest.mark.asyncio
    async def test_to_namespaces_edit(self, adapter):
        app_name = "app-name"
        api_request = NamespaceEditRequest(
            app_name=app_name,
            name="namespace-name",
            data=NamespaceEditData(display_name="display_name"),
        )
        result = await adapter.to_namespace_edit(api_request)
        assert result == NamespaceEditQuery(
            name="namespace-name",
            display_name="display_name",
            app_name=app_name,
        )


class TestSQLNamespacePersistenceAdapter:
    @pytest_asyncio.fixture
    async def namespace_sql_adapter(
        self, registry_test_adapters
    ) -> SQLNamespacePersistenceAdapter:
        return await registry_test_adapters.request_port(NamespacePersistencePort)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create(
        self, namespace_sql_adapter: SQLNamespacePersistenceAdapter, create_app
    ):
        async with namespace_sql_adapter.session() as session:
            app = await create_app(session)
        namespace = await namespace_sql_adapter.create(
            Namespace(app_name=app.name, name="namespace", display_name="Namespace")
        )
        assert namespace == Namespace(
            app_name=app.name, name="namespace", display_name="Namespace"
        )
        async with namespace_sql_adapter.session() as session:
            result = (await session.scalars(select(DBNamespace))).one()
            assert result.name == "namespace"
            assert result.display_name == "Namespace"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_exists_error(
        self,
        namespace_sql_adapter: SQLNamespacePersistenceAdapter,
        create_app,
        create_namespace,
    ):
        async with namespace_sql_adapter.session() as session:
            app = await create_app(session)
            namespace = await create_namespace(session, app_name=app.name)
        with pytest.raises(ObjectExistsError):
            await namespace_sql_adapter.create(
                Namespace(
                    app_name=app.name, name=namespace.name, display_name="Namespace"
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_parent_not_found_error(
        self,
        namespace_sql_adapter: SQLNamespacePersistenceAdapter,
        create_namespace,
    ):
        with pytest.raises(
            ParentNotFoundError,
            match="The app/namespace of the object to be created does not exist.",
        ):
            await namespace_sql_adapter.create(
                Namespace(app_name="app", name="namespace", display_name="Namespace")
            )

    @pytest.mark.asyncio
    async def test_create_unhandled_error(
        self, namespace_sql_adapter: SQLNamespacePersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await namespace_sql_adapter.create(
                Namespace(app_name="foo", name="namespace", display_name="Namespace")
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one(
        self,
        namespace_sql_adapter: SQLNamespacePersistenceAdapter,
        create_app,
        create_namespace,
    ):
        async with namespace_sql_adapter.session() as session:
            db_app = await create_app(session)
            db_namespace = await create_namespace(session, app_name=db_app.name)
        namespace = await namespace_sql_adapter.read_one(
            NamespaceGetQuery(app_name=db_app.name, name=db_namespace.name)
        )
        assert namespace.name == db_namespace.name
        assert namespace.display_name == db_namespace.display_name
        assert namespace.app_name == db_app.name

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one_none(
        self,
        namespace_sql_adapter: SQLNamespacePersistenceAdapter,
        create_app,
        create_namespace,
    ):
        async with namespace_sql_adapter.session() as session:
            app = await create_app(session)
            await create_namespace(session, app_name=app.name)
        with pytest.raises(ObjectNotFoundError):
            await namespace_sql_adapter.read_one(
                NamespaceGetQuery(app_name=app.name, name="other_namespace")
            )

    @pytest.mark.asyncio
    async def test_read_one_unhandled_error(
        self, namespace_sql_adapter: SQLNamespacePersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await namespace_sql_adapter.read_one(
                NamespaceGetQuery(app_name="app", name="other_namespace")
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_many_empty(
        self, namespace_sql_adapter: SQLNamespacePersistenceAdapter
    ):
        result = await namespace_sql_adapter.read_many(
            NamespacesGetQuery(pagination=PaginationRequest(query_offset=0))
        )
        assert result == PersistenceGetManyResult(total_count=0, objects=[])

    @pytest.mark.asyncio
    async def test_read_many_unhandled_error(
        self, namespace_sql_adapter: SQLNamespacePersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await namespace_sql_adapter.read_many(
                NamespacesGetQuery(pagination=PaginationRequest(query_offset=0))
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
        self,
        namespace_sql_adapter: SQLNamespacePersistenceAdapter,
        create_namespaces,
        limit,
        offset,
    ):
        async with namespace_sql_adapter.session() as session:
            namespaces = await create_namespaces(
                session, namespaces_per_app=10, num_apps=10
            )
            namespaces.sort(key=lambda x: x.name)
        result = await namespace_sql_adapter.read_many(
            NamespacesGetQuery(
                pagination=PaginationRequest(query_offset=offset, query_limit=limit)
            )
        )
        selected_slice = (
            namespaces[offset : offset + limit] if limit else namespaces[offset:]
        )
        assert result.total_count == 100
        assert [obj.name for obj in result.objects] == [
            obj.name for obj in selected_slice
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update(
        self, namespace_sql_adapter: SQLNamespacePersistenceAdapter, create_namespaces
    ):
        async with namespace_sql_adapter.session() as session:
            db_namespace = (await create_namespaces(session, 1, 1))[0]
        result = await namespace_sql_adapter.update(
            Namespace(
                app_name=db_namespace.app.name,
                name=db_namespace.name,
                display_name="NEW DISPLAY NAME",
            )
        )
        assert result == Namespace(
            app_name=db_namespace.app.name,
            name=db_namespace.name,
            display_name="NEW DISPLAY NAME",
        )
        async with namespace_sql_adapter.session() as session:
            result = (await session.scalars(select(DBNamespace))).one()
            assert result.name == result.name
            assert result.display_name == result.display_name

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update_object_not_found_error(
        self, namespace_sql_adapter: SQLNamespacePersistenceAdapter, create_namespaces
    ):
        async with namespace_sql_adapter.session() as session:
            await create_namespaces(session, 1, 1)
        with pytest.raises(
            ObjectNotFoundError,
            match="No app with the identifier 'app:some_app' could be found.",
        ):
            await namespace_sql_adapter.update(
                Namespace(
                    app_name="app", name="some_app", display_name="NEW DISPLAY NAME"
                )
            )
