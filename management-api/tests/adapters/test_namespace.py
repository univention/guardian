import pytest
import pytest_asyncio
from guardian_management_api.adapters.namespace import SQLNamespacePersistenceAdapter
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
    NamespaceGetQuery,
    NamespacesGetQuery,
)
from guardian_management_api.models.sql_persistence import (
    DBNamespace,
    SQLPersistenceAdapterSettings,
)
from sqlalchemy import select


class TestSQLNamespacePersistenceAdapter:
    @pytest_asyncio.fixture
    async def namespace_sql_adapter(self, sqlite_url) -> SQLNamespacePersistenceAdapter:
        adapter = SQLNamespacePersistenceAdapter()
        await adapter.configure(
            SQLPersistenceAdapterSettings(dialect="sqlite", db_name=sqlite_url)
        )
        return adapter

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
        app = await namespace_sql_adapter.read_one(
            NamespaceGetQuery(app_name=app.name, name="other_namespace")
        )
        assert app is None

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
