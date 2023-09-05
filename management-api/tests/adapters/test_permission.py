# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
import pytest_asyncio
from guardian_management_api.adapters.permission import SQLPermissionPersistenceAdapter
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
from guardian_management_api.models.permission import (
    Permission,
    PermissionGetQuery,
    PermissionsGetQuery,
)
from guardian_management_api.models.sql_persistence import (
    DBPermission,
)
from guardian_management_api.ports.permission import PermissionPersistencePort
from sqlalchemy import select


class TestSQLPermissionPersistenceAdapter:
    @pytest_asyncio.fixture
    async def permission_sql_adapter(
        self, register_test_adapters
    ) -> SQLPermissionPersistenceAdapter:
        return await register_test_adapters.request_port(PermissionPersistencePort)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create(
        self, permission_sql_adapter: SQLPermissionPersistenceAdapter, create_namespaces
    ):
        async with permission_sql_adapter.session() as session:
            namespace = (await create_namespaces(session, 1))[0]
        permission = await permission_sql_adapter.create(
            Permission(
                app_name=namespace.app.name,
                namespace_name=namespace.name,
                name="permission",
                display_name="Permission",
            )
        )
        assert permission == Permission(
            app_name=namespace.app.name,
            namespace_name=namespace.name,
            name="permission",
            display_name="Permission",
        )
        async with permission_sql_adapter.session() as session:
            result = (await session.scalars(select(DBPermission))).one()
            assert result.namespace_id == namespace.id
            assert result.name == "permission"
            assert result.display_name == "Permission"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_exists_error(
        self,
        permission_sql_adapter: SQLPermissionPersistenceAdapter,
        create_permission,
        create_namespaces,
    ):
        async with permission_sql_adapter.session() as session:
            namespace = (await create_namespaces(session, 1))[0]
            permission = await create_permission(
                session, app_name=namespace.app.name, namespace_name=namespace.name
            )
        with pytest.raises(ObjectExistsError):
            await permission_sql_adapter.create(
                Permission(
                    app_name=permission.namespace.app.name,
                    namespace_name=permission.namespace.name,
                    name=permission.name,
                    display_name="Permission",
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_app_not_found_error(
        self,
        permission_sql_adapter: SQLPermissionPersistenceAdapter,
    ):
        with pytest.raises(
            ParentNotFoundError,
            match="The app of the object to be created does not exist.",
        ):
            await permission_sql_adapter.create(
                Permission(
                    app_name="app",
                    namespace_name="namespace",
                    name="permission",
                    display_name="Permission",
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_namespace_not_found_error(
        self, permission_sql_adapter: SQLPermissionPersistenceAdapter, create_apps
    ):
        async with permission_sql_adapter.session() as session:
            app = (await create_apps(session, 1))[0]
        with pytest.raises(
            ParentNotFoundError,
            match="The namespace of the object to be created does not exist.",
        ):
            await permission_sql_adapter.create(
                Permission(
                    app_name=app.name,
                    namespace_name="namespace",
                    name="permission",
                    display_name="Permission",
                )
            )

    @pytest.mark.asyncio
    async def test_create_unhandled_error(
        self, permission_sql_adapter: SQLPermissionPersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await permission_sql_adapter.create(
                Permission(
                    app_name="foo",
                    namespace_name="bar",
                    name="permission",
                    display_name="Permission",
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one(
        self,
        permission_sql_adapter: SQLPermissionPersistenceAdapter,
        create_permissions,
    ):
        async with permission_sql_adapter.session() as session:
            db_permission = (await create_permissions(session, 1))[0]
        permission = await permission_sql_adapter.read_one(
            PermissionGetQuery(
                app_name=db_permission.namespace.app.name,
                namespace_name=db_permission.namespace.name,
                name=db_permission.name,
            )
        )
        assert permission.app_name == db_permission.namespace.app.name
        assert permission.namespace_name == db_permission.namespace.name
        assert permission.name == db_permission.name
        assert permission.display_name == db_permission.display_name

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one_none(
        self,
        permission_sql_adapter: SQLPermissionPersistenceAdapter,
    ):
        with pytest.raises(ObjectNotFoundError):
            await permission_sql_adapter.read_one(
                PermissionGetQuery(
                    app_name="foo", namespace_name="bar", name="permission"
                )
            )

    @pytest.mark.asyncio
    async def test_read_one_unhandled_error(
        self, permission_sql_adapter: SQLPermissionPersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await permission_sql_adapter.read_one(
                PermissionGetQuery(
                    app_name="foo", namespace_name="bar", name="permission"
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_many_empty(
        self, permission_sql_adapter: SQLPermissionPersistenceAdapter
    ):
        result = await permission_sql_adapter.read_many(
            PermissionsGetQuery(pagination=PaginationRequest(query_offset=0))
        )
        assert result == PersistenceGetManyResult(total_count=0, objects=[])

    @pytest.mark.asyncio
    async def test_read_many_unhandled_error(
        self, permission_sql_adapter: SQLPermissionPersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await permission_sql_adapter.read_many(
                PermissionsGetQuery(pagination=PaginationRequest(query_offset=0))
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
        permission_sql_adapter: SQLPermissionPersistenceAdapter,
        create_permissions,
        limit,
        offset,
    ):
        async with permission_sql_adapter.session() as session:
            permissions = await create_permissions(session, 5, 2, 10)
            permissions.sort(key=lambda x: x.name)
        result = await permission_sql_adapter.read_many(
            PermissionsGetQuery(
                pagination=PaginationRequest(query_offset=offset, query_limit=limit)
            )
        )
        selected_slice = (
            permissions[offset : offset + limit] if limit else permissions[offset:]
        )
        assert result.total_count == 100
        assert [obj.name for obj in result.objects] == [
            obj.name for obj in selected_slice
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update(
        self,
        permission_sql_adapter: SQLPermissionPersistenceAdapter,
        create_permissions,
    ):
        async with permission_sql_adapter.session() as session:
            db_permission = (await create_permissions(session, 1))[0]
        result = await permission_sql_adapter.update(
            Permission(
                app_name=db_permission.namespace.app.name,
                namespace_name=db_permission.namespace.name,
                name=db_permission.name,
                display_name="NEW DISPLAY NAME",
            )
        )
        assert result == Permission(
            app_name=db_permission.namespace.app.name,
            namespace_name=db_permission.namespace.name,
            name=db_permission.name,
            display_name="NEW DISPLAY NAME",
        )
        async with permission_sql_adapter.session() as session:
            result = (await session.scalars(select(DBPermission))).one()
            assert result.name == db_permission.name
            assert result.display_name == "NEW DISPLAY NAME"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update_object_not_found_error(
        self,
        permission_sql_adapter: SQLPermissionPersistenceAdapter,
        create_permissions,
    ):
        async with permission_sql_adapter.session() as session:
            await create_permissions(session, 1)
        with pytest.raises(
            ObjectNotFoundError,
            match="No permission with the identifier 'app:namespace:permission' could be found.",
        ):
            await permission_sql_adapter.update(
                Permission(
                    app_name="app",
                    namespace_name="namespace",
                    name="permission",
                    display_name="NEW DISPLAY NAME",
                )
            )
