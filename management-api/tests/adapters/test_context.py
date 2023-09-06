# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
import pytest_asyncio
from guardian_management_api.adapters.context import (
    FastAPIContextAPIAdapter,
    SQLContextPersistenceAdapter,
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
from guardian_management_api.models.context import (
    Context,
    ContextCreateQuery,
    ContextGetQuery,
    ContextsGetQuery,
)
from guardian_management_api.models.routers.context import (
    Context as ResponseContext,
)
from guardian_management_api.models.routers.context import (
    ContextCreateData,
    ContextCreateRequest,
    ContextGetRequest,
    ContextSingleResponse,
)
from guardian_management_api.models.sql_persistence import (
    DBContext,
)
from guardian_management_api.ports.context import ContextPersistencePort
from sqlalchemy import select


class TestFastAPIContextAdapter:
    @pytest.fixture(autouse=True)
    def adapter(self):
        return FastAPIContextAPIAdapter()

    @pytest.mark.asyncio
    async def test_to_context_create(self, adapter):
        app_name = "app-name"
        namespace_name = "namespace-name"
        api_request = ContextCreateRequest(
            app_name=app_name,
            namespace_name=namespace_name,
            data=ContextCreateData(display_name="display_name", name="context-name"),
        )
        result = await adapter.to_context_create(api_request)
        assert result == ContextCreateQuery(
            name="context-name",
            display_name="display_name",
            app_name=app_name,
            namespace_name=namespace_name,
        )

    @pytest.mark.asyncio
    async def test_to_api_create_response(self, adapter):
        context = Context(
            name="name",
            display_name="display_name",
            app_name="app-name",
            namespace_name="namespace-name",
        )
        result = await adapter.to_api_create_response(context)
        assert result == ContextSingleResponse(
            context=ResponseContext(
                name=context.name,
                app_name=context.app_name,
                display_name=context.display_name,
                namespace_name=context.namespace_name,
                resource_url=f"{COMPLETE_URL}/contexts/{context.app_name}/{context.namespace_name}/{context.name}",
            )
        )

    @pytest.mark.asyncio
    async def test_to_context_get(self, adapter):
        app_name = "app-name"
        api_request = ContextGetRequest(
            app_name=app_name,
            name="context-name",
            namespace_name="namespace-name",
        )
        result = await adapter.to_context_get(api_request)
        assert result == ContextGetQuery(
            name="context-name",
            app_name=app_name,
            namespace_name="namespace-name",
        )

    @pytest.mark.asyncio
    async def test_to_api_get_response(self, adapter):
        context = Context(
            name="name",
            display_name="display_name",
            app_name="app-name",
            namespace_name="namespace-name",
        )
        result = await adapter.to_api_get_response(context)
        assert result == ContextSingleResponse(
            context=ResponseContext(
                name=context.name,
                app_name=context.app_name,
                display_name=context.display_name,
                namespace_name=context.namespace_name,
                resource_url=f"{COMPLETE_URL}/contexts/{context.app_name}/{context.namespace_name}/{context.name}",
            )
        )


class TestSQLContextPersistenceAdapter:
    @pytest_asyncio.fixture
    async def context_sql_adapter(
        self, register_test_adapters
    ) -> SQLContextPersistenceAdapter:
        return await register_test_adapters.request_port(ContextPersistencePort)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create(
        self, context_sql_adapter: SQLContextPersistenceAdapter, create_namespaces
    ):
        async with context_sql_adapter.session() as session:
            namespace = (await create_namespaces(session, 1))[0]
        context = await context_sql_adapter.create(
            Context(
                app_name=namespace.app.name,
                namespace_name=namespace.name,
                name="context",
                display_name="Context",
            )
        )
        assert context == Context(
            app_name=namespace.app.name,
            namespace_name=namespace.name,
            name="context",
            display_name="Context",
        )
        async with context_sql_adapter.session() as session:
            result = (await session.scalars(select(DBContext))).one()
            assert result.namespace_id == namespace.id
            assert result.name == "context"
            assert result.display_name == "Context"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_exists_error(
        self,
        context_sql_adapter: SQLContextPersistenceAdapter,
        create_context,
        create_namespaces,
    ):
        async with context_sql_adapter.session() as session:
            namespace = (await create_namespaces(session, 1))[0]
            context = await create_context(
                session, app_name=namespace.app.name, namespace_name=namespace.name
            )
        with pytest.raises(ObjectExistsError):
            await context_sql_adapter.create(
                Context(
                    app_name=context.namespace.app.name,
                    namespace_name=context.namespace.name,
                    name=context.name,
                    display_name="Context",
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_app_not_found_error(
        self,
        context_sql_adapter: SQLContextPersistenceAdapter,
    ):
        with pytest.raises(
            ParentNotFoundError,
            match="The app of the object to be created does not exist.",
        ):
            await context_sql_adapter.create(
                Context(
                    app_name="app",
                    namespace_name="namespace",
                    name="context",
                    display_name="Context",
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_namespace_not_found_error(
        self, context_sql_adapter: SQLContextPersistenceAdapter, create_apps
    ):
        async with context_sql_adapter.session() as session:
            app = (await create_apps(session, 1))[0]
        with pytest.raises(
            ParentNotFoundError,
            match="The namespace of the object to be created does not exist.",
        ):
            await context_sql_adapter.create(
                Context(
                    app_name=app.name,
                    namespace_name="namespace",
                    name="context",
                    display_name="Context",
                )
            )

    @pytest.mark.asyncio
    async def test_create_unhandled_error(
        self, context_sql_adapter: SQLContextPersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await context_sql_adapter.create(
                Context(
                    app_name="foo",
                    namespace_name="bar",
                    name="context",
                    display_name="Context",
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one(
        self,
        context_sql_adapter: SQLContextPersistenceAdapter,
        create_contexts,
    ):
        async with context_sql_adapter.session() as session:
            db_context = (await create_contexts(session, 1))[0]
        context = await context_sql_adapter.read_one(
            ContextGetQuery(
                app_name=db_context.namespace.app.name,
                namespace_name=db_context.namespace.name,
                name=db_context.name,
            )
        )
        assert context.app_name == db_context.namespace.app.name
        assert context.namespace_name == db_context.namespace.name
        assert context.name == db_context.name
        assert context.display_name == db_context.display_name

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one_none(
        self,
        context_sql_adapter: SQLContextPersistenceAdapter,
    ):
        with pytest.raises(ObjectNotFoundError):
            await context_sql_adapter.read_one(
                ContextGetQuery(app_name="foo", namespace_name="bar", name="context")
            )

    @pytest.mark.asyncio
    async def test_read_one_unhandled_error(
        self, context_sql_adapter: SQLContextPersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await context_sql_adapter.read_one(
                ContextGetQuery(app_name="foo", namespace_name="bar", name="context")
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_many_empty(
        self, context_sql_adapter: SQLContextPersistenceAdapter
    ):
        result = await context_sql_adapter.read_many(
            ContextsGetQuery(pagination=PaginationRequest(query_offset=0))
        )
        assert result == PersistenceGetManyResult(total_count=0, objects=[])

    @pytest.mark.asyncio
    async def test_read_many_unhandled_error(
        self, context_sql_adapter: SQLContextPersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await context_sql_adapter.read_many(
                ContextsGetQuery(pagination=PaginationRequest(query_offset=0))
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
        context_sql_adapter: SQLContextPersistenceAdapter,
        create_contexts,
        limit,
        offset,
    ):
        async with context_sql_adapter.session() as session:
            contexts = await create_contexts(session, 5, 2, 10)
            contexts.sort(key=lambda x: x.name)
        result = await context_sql_adapter.read_many(
            ContextsGetQuery(
                pagination=PaginationRequest(query_offset=offset, query_limit=limit)
            )
        )
        selected_slice = (
            contexts[offset : offset + limit] if limit else contexts[offset:]
        )
        assert result.total_count == 100
        assert [obj.name for obj in result.objects] == [
            obj.name for obj in selected_slice
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update(
        self,
        context_sql_adapter: SQLContextPersistenceAdapter,
        create_contexts,
    ):
        async with context_sql_adapter.session() as session:
            db_context = (await create_contexts(session, 1))[0]
        result = await context_sql_adapter.update(
            Context(
                app_name=db_context.namespace.app.name,
                namespace_name=db_context.namespace.name,
                name=db_context.name,
                display_name="NEW DISPLAY NAME",
            )
        )
        assert result == Context(
            app_name=db_context.namespace.app.name,
            namespace_name=db_context.namespace.name,
            name=db_context.name,
            display_name="NEW DISPLAY NAME",
        )
        async with context_sql_adapter.session() as session:
            result = (await session.scalars(select(DBContext))).one()
            assert result.name == db_context.name
            assert result.display_name == "NEW DISPLAY NAME"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update_object_not_found_error(
        self,
        context_sql_adapter: SQLContextPersistenceAdapter,
        create_contexts,
    ):
        async with context_sql_adapter.session() as session:
            await create_contexts(session, 1)
        with pytest.raises(
            ObjectNotFoundError,
            match="No context with the identifier 'app:namespace:context' could be found.",
        ):
            await context_sql_adapter.update(
                Context(
                    app_name="app",
                    namespace_name="namespace",
                    name="context",
                    display_name="NEW DISPLAY NAME",
                )
            )
