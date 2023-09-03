# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
import pytest_asyncio
from guardian_management_api.adapters.role import SQLRolePersistenceAdapter
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
from guardian_management_api.models.role import (
    Role,
    RoleGetQuery,
    RolesGetQuery,
)
from guardian_management_api.models.sql_persistence import (
    DBRole,
    SQLPersistenceAdapterSettings,
)
from sqlalchemy import select


class TestSQLRolePersistenceAdapter:
    @pytest_asyncio.fixture
    async def role_sql_adapter(self, sqlite_url) -> SQLRolePersistenceAdapter:
        adapter = SQLRolePersistenceAdapter()
        await adapter.configure(
            SQLPersistenceAdapterSettings(dialect="sqlite", db_name=sqlite_url)
        )
        return adapter

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create(
        self, role_sql_adapter: SQLRolePersistenceAdapter, create_namespaces
    ):
        async with role_sql_adapter.session() as session:
            namespace = (await create_namespaces(session, 1))[0]
        role = await role_sql_adapter.create(
            Role(
                app_name=namespace.app.name,
                namespace_name=namespace.name,
                name="role",
                display_name="Role",
            )
        )
        assert role == Role(
            app_name=namespace.app.name,
            namespace_name=namespace.name,
            name="role",
            display_name="Role",
        )
        async with role_sql_adapter.session() as session:
            result = (await session.scalars(select(DBRole))).one()
            assert result.namespace_id == namespace.id
            assert result.name == "role"
            assert result.display_name == "Role"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_exists_error(
        self,
        role_sql_adapter: SQLRolePersistenceAdapter,
        create_role,
        create_namespaces,
    ):
        async with role_sql_adapter.session() as session:
            namespace = (await create_namespaces(session, 1))[0]
            role = await create_role(
                session, app_name=namespace.app.name, namespace_name=namespace.name
            )
        with pytest.raises(ObjectExistsError):
            await role_sql_adapter.create(
                Role(
                    app_name=role.namespace.app.name,
                    namespace_name=role.namespace.name,
                    name=role.name,
                    display_name="Role",
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_app_not_found_error(
        self,
        role_sql_adapter: SQLRolePersistenceAdapter,
    ):
        with pytest.raises(
            ParentNotFoundError,
            match="The app of the object to be created does not exist.",
        ):
            await role_sql_adapter.create(
                Role(
                    app_name="app",
                    namespace_name="namespace",
                    name="role",
                    display_name="Role",
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_namespace_not_found_error(
        self, role_sql_adapter: SQLRolePersistenceAdapter, create_apps
    ):
        async with role_sql_adapter.session() as session:
            app = (await create_apps(session, 1))[0]
        with pytest.raises(
            ParentNotFoundError,
            match="The namespace of the object to be created does not exist.",
        ):
            await role_sql_adapter.create(
                Role(
                    app_name=app.name,
                    namespace_name="namespace",
                    name="role",
                    display_name="Role",
                )
            )

    @pytest.mark.asyncio
    async def test_create_unhandled_error(
        self, role_sql_adapter: SQLRolePersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await role_sql_adapter.create(
                Role(
                    app_name="foo",
                    namespace_name="bar",
                    name="role",
                    display_name="Role",
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one(
        self,
        role_sql_adapter: SQLRolePersistenceAdapter,
        create_roles,
    ):
        async with role_sql_adapter.session() as session:
            db_role = (await create_roles(session, 1))[0]
        role = await role_sql_adapter.read_one(
            RoleGetQuery(
                app_name=db_role.namespace.app.name,
                namespace_name=db_role.namespace.name,
                name=db_role.name,
            )
        )
        assert role.app_name == db_role.namespace.app.name
        assert role.namespace_name == db_role.namespace.name
        assert role.name == db_role.name
        assert role.display_name == db_role.display_name

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one_none(
        self,
        role_sql_adapter: SQLRolePersistenceAdapter,
    ):
        with pytest.raises(ObjectNotFoundError):
            await role_sql_adapter.read_one(
                RoleGetQuery(app_name="foo", namespace_name="bar", name="role")
            )

    @pytest.mark.asyncio
    async def test_read_one_unhandled_error(
        self, role_sql_adapter: SQLRolePersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await role_sql_adapter.read_one(
                RoleGetQuery(app_name="foo", namespace_name="bar", name="role")
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_many_empty(self, role_sql_adapter: SQLRolePersistenceAdapter):
        result = await role_sql_adapter.read_many(
            RolesGetQuery(pagination=PaginationRequest(query_offset=0))
        )
        assert result == PersistenceGetManyResult(total_count=0, objects=[])

    @pytest.mark.asyncio
    async def test_read_many_unhandled_error(
        self, role_sql_adapter: SQLRolePersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await role_sql_adapter.read_many(
                RolesGetQuery(pagination=PaginationRequest(query_offset=0))
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
        role_sql_adapter: SQLRolePersistenceAdapter,
        create_roles,
        limit,
        offset,
    ):
        async with role_sql_adapter.session() as session:
            roles = await create_roles(session, 5, 2, 10)
            roles.sort(key=lambda x: x.name)
        result = await role_sql_adapter.read_many(
            RolesGetQuery(
                pagination=PaginationRequest(query_offset=offset, query_limit=limit)
            )
        )
        selected_slice = roles[offset : offset + limit] if limit else roles[offset:]
        assert result.total_count == 100
        assert [obj.name for obj in result.objects] == [
            obj.name for obj in selected_slice
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update(
        self,
        role_sql_adapter: SQLRolePersistenceAdapter,
        create_roles,
    ):
        async with role_sql_adapter.session() as session:
            db_role = (await create_roles(session, 1))[0]
        result = await role_sql_adapter.update(
            Role(
                app_name=db_role.namespace.app.name,
                namespace_name=db_role.namespace.name,
                name=db_role.name,
                display_name="NEW DISPLAY NAME",
            )
        )
        assert result == Role(
            app_name=db_role.namespace.app.name,
            namespace_name=db_role.namespace.name,
            name=db_role.name,
            display_name="NEW DISPLAY NAME",
        )
        async with role_sql_adapter.session() as session:
            result = (await session.scalars(select(DBRole))).one()
            assert result.name == db_role.name
            assert result.display_name == "NEW DISPLAY NAME"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update_object_not_found_error(
        self,
        role_sql_adapter: SQLRolePersistenceAdapter,
        create_roles,
    ):
        async with role_sql_adapter.session() as session:
            await create_roles(session, 1)
        with pytest.raises(
            ObjectNotFoundError,
            match="No role with the identifier 'app:namespace:role' could be found.",
        ):
            await role_sql_adapter.update(
                Role(
                    app_name="app",
                    namespace_name="namespace",
                    name="role",
                    display_name="NEW DISPLAY NAME",
                )
            )
