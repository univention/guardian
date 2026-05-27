# Copyright (C) 2023-2026 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
import pytest_asyncio
from guardian_management_api.adapters.app import SQLAppPersistenceAdapter
from guardian_management_api.adapters.namespace import SQLNamespacePersistenceAdapter
from guardian_management_api.errors import ObjectNotFoundError
from guardian_management_api.models.app import AppGetQuery
from guardian_management_api.models.namespace import NamespaceGetQuery
from guardian_management_api.models.sql_persistence import DBApp, DBNamespace
from guardian_management_api.ports.app import AppPersistencePort
from guardian_management_api.ports.namespace import NamespacePersistencePort
from sqlalchemy import select


class TestSQLAppPersistenceAdapterDelete:
    @pytest_asyncio.fixture
    async def app_sql_adapter(self, registry_test_adapters) -> SQLAppPersistenceAdapter:
        return await registry_test_adapters.request_port(AppPersistencePort)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete(self, app_sql_adapter: SQLAppPersistenceAdapter, create_apps):
        async with app_sql_adapter.session() as session:
            db_app = (await create_apps(session, 1))[0]
        assert (await app_sql_adapter.delete(AppGetQuery(name=db_app.name))) is None
        async with app_sql_adapter.session() as session:
            assert (
                await session.scalar(select(DBApp).where(DBApp.name == db_app.name))
            ) is None

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_not_found_error(
        self, app_sql_adapter: SQLAppPersistenceAdapter
    ):
        with pytest.raises(ObjectNotFoundError):
            await app_sql_adapter.delete(AppGetQuery(name="nonexistent"))

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_dependencies_empty(
        self, app_sql_adapter: SQLAppPersistenceAdapter, create_apps
    ):
        async with app_sql_adapter.session() as session:
            db_app = (await create_apps(session, 1))[0]
        result = await app_sql_adapter.read_dependencies(AppGetQuery(name=db_app.name))
        assert result == []

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_dependencies_with_namespace(
        self, app_sql_adapter: SQLAppPersistenceAdapter, create_namespaces
    ):
        async with app_sql_adapter.session() as session:
            db_namespace = (await create_namespaces(session, 1))[0]
        result = await app_sql_adapter.read_dependencies(
            AppGetQuery(name=db_namespace.app.name)
        )
        assert len(result) == 1
        assert result[0].name == db_namespace.name

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_dependencies_not_found_error(
        self, app_sql_adapter: SQLAppPersistenceAdapter
    ):
        with pytest.raises(ObjectNotFoundError):
            await app_sql_adapter.read_dependencies(AppGetQuery(name="nonexistent"))


class TestSQLNamespacePersistenceAdapterDelete:
    @pytest_asyncio.fixture
    async def namespace_sql_adapter(
        self, registry_test_adapters
    ) -> SQLNamespacePersistenceAdapter:
        return await registry_test_adapters.request_port(NamespacePersistencePort)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete(
        self, namespace_sql_adapter: SQLNamespacePersistenceAdapter, create_namespaces
    ):
        async with namespace_sql_adapter.session() as session:
            db_namespace = (await create_namespaces(session, 1))[0]
        assert (
            await namespace_sql_adapter.delete(
                NamespaceGetQuery(
                    name=db_namespace.name, app_name=db_namespace.app.name
                )
            )
        ) is None
        async with namespace_sql_adapter.session() as session:
            assert (
                await session.scalar(
                    select(DBNamespace).where(DBNamespace.name == db_namespace.name)
                )
            ) is None

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_not_found_error(
        self, namespace_sql_adapter: SQLNamespacePersistenceAdapter
    ):
        with pytest.raises(ObjectNotFoundError):
            await namespace_sql_adapter.delete(
                NamespaceGetQuery(name="nonexistent", app_name="nonexistent")
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_dependencies_empty(
        self, namespace_sql_adapter: SQLNamespacePersistenceAdapter, create_namespaces
    ):
        async with namespace_sql_adapter.session() as session:
            db_namespace = (await create_namespaces(session, 1))[0]
        result = await namespace_sql_adapter.read_dependencies(
            NamespaceGetQuery(name=db_namespace.name, app_name=db_namespace.app.name)
        )
        assert result == []

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_dependencies_with_children(
        self,
        namespace_sql_adapter: SQLNamespacePersistenceAdapter,
        create_roles,
    ):
        async with namespace_sql_adapter.session() as session:
            db_roles = await create_roles(session, 2)
        db_namespace = db_roles[0].namespace
        result = await namespace_sql_adapter.read_dependencies(
            NamespaceGetQuery(name=db_namespace.name, app_name=db_namespace.app.name)
        )
        assert len(result) == 2
        prefix = f"role:{db_namespace.app.name}:{db_namespace.name}:"
        assert all(isinstance(r, str) and r.startswith(prefix) for r in result)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_dependencies_not_found_error(
        self, namespace_sql_adapter: SQLNamespacePersistenceAdapter
    ):
        with pytest.raises(ObjectNotFoundError):
            await namespace_sql_adapter.read_dependencies(
                NamespaceGetQuery(name="nonexistent", app_name="nonexistent")
            )
