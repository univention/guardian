# Copyright (C) 2023-2026 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
from guardian_management_api.main import app
from guardian_management_api.models.sql_persistence import DBApp, DBNamespace
from sqlalchemy import func, select


@pytest.mark.e2e
class TestAppDeleteEndpoint:
    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_app(self, client, create_apps, sqlalchemy_mixin):
        async with sqlalchemy_mixin.session() as session:
            db_app = (await create_apps(session, 1))[0]
        result = client.delete(app.url_path_for("delete_app", name=db_app.name))
        assert result.status_code == 204, result.json()
        async with sqlalchemy_mixin.session() as session:
            assert (await session.scalar(select(func.count(DBApp.id)))) == 0

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_app_404(self, client):
        result = client.delete(app.url_path_for("delete_app", name="nonexistent"))
        assert result.status_code == 404, result.json()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_app_with_namespace_returns_409(
        self, client, create_namespaces, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_namespace = (await create_namespaces(session, 1))[0]
        result = client.delete(
            app.url_path_for("delete_app", name=db_namespace.app.name)
        )
        assert result.status_code == 409, result.json()
        # App must still exist
        async with sqlalchemy_mixin.session() as session:
            assert (await session.scalar(select(func.count(DBApp.id)))) == 1


@pytest.mark.e2e
class TestNamespaceDeleteEndpoint:
    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_namespace(self, client, create_namespaces, sqlalchemy_mixin):
        async with sqlalchemy_mixin.session() as session:
            db_namespace = (await create_namespaces(session, 1))[0]
        result = client.delete(
            app.url_path_for(
                "delete_namespace",
                app_name=db_namespace.app.name,
                name=db_namespace.name,
            )
        )
        assert result.status_code == 204, result.json()
        async with sqlalchemy_mixin.session() as session:
            assert (await session.scalar(select(func.count(DBNamespace.id)))) == 0

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_namespace_404(self, client, create_apps, sqlalchemy_mixin):
        async with sqlalchemy_mixin.session() as session:
            db_app = (await create_apps(session, 1))[0]
        result = client.delete(
            app.url_path_for(
                "delete_namespace", app_name=db_app.name, name="nonexistent"
            )
        )
        assert result.status_code == 404, result.json()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_namespace_with_children_returns_409(
        self, client, create_permissions, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_permissions = await create_permissions(session, 1)
        db_namespace = db_permissions[0].namespace
        result = client.delete(
            app.url_path_for(
                "delete_namespace",
                app_name=db_namespace.app.name,
                name=db_namespace.name,
            )
        )
        assert result.status_code == 409, result.json()
        # Namespace must still exist
        async with sqlalchemy_mixin.session() as session:
            assert (await session.scalar(select(func.count(DBNamespace.id)))) == 1
