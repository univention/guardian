# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
from guardian_management_api.adapters.sql_persistence import (
    SQLAlchemyMixin,
    error_guard,
)
from guardian_management_api.errors import (
    ObjectExistsError,
    ParentNotFoundError,
    PersistenceError,
)
from guardian_management_api.models.sql_persistence import (
    DBApp,
    DBNamespace,
    DBPermission,
    DBRole,
)
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


@pytest.mark.asyncio
async def test_error_guard():
    async def test_func():
        raise SQLAlchemyError()

    wrapped = error_guard(test_func)
    with pytest.raises(PersistenceError, match="An unidentified error occurred."):
        await wrapped()


@pytest.mark.asyncio
async def test_error_guard_uncaught_exception():
    async def test_func():
        raise ValueError("ORIGINAL_ERROR")

    wrapped = error_guard(test_func)
    with pytest.raises(ValueError, match="ORIGINAL_ERROR"):
        await wrapped()


class TestSQLAlchemyMixin:
    def test_init(self):
        obj = SQLAlchemyMixin()
        assert obj._sql_engine is None
        assert obj._session is None
        assert obj._db_string == ""

    @pytest.mark.parametrize(
        "dialect,host,port,db_name,username,password,expected",
        [
            ("sqlite", "", "", "", "", "", "sqlite+aiosqlite://"),
            ("sqlite", "a", "b", "c", "d", "e", "sqlite+aiosqlite:///c"),
            ("postgresql", "a", "", "c", "d", "e", "postgresql+asyncpg://d:e@a/c"),
            ("postgresql", "a", "b", "c", "d", "e", "postgresql+asyncpg://d:e@a:b/c"),
            ("mysql", "a", "", "c", "d", "e", "mysql+aiomysql://d:e@a/c"),
            ("mysql", "a", "b", "c", "d", "e", "mysql+aiomysql://d:e@a:b/c"),
        ],
    )
    def test_create_db_string(
        self, dialect, host, port, db_name, username, password, expected
    ):
        if dialect in ("mysql, postgresql"):
            pytest.skip(
                "Reactivate with univention/components/authorization-engine/guardian#98"
            )
        assert (
            SQLAlchemyMixin.create_db_string(
                dialect, host, port, db_name, username, password
            )
            == expected
        )

    def test_create_db_string_unsupported_dialect(self):
        with pytest.raises(ValueError, match="The dialect FOO is not supported."):
            SQLAlchemyMixin.create_db_string("FOO", "", "", "", "", "")

    @pytest.mark.parametrize("dialect", ["mysql", "postgresql"])
    @pytest.mark.parametrize(
        "host,port,db_name,username,password",
        [
            ("", "", "", "", ""),
            ("a", "", "", "", ""),
            ("", "b", "", "", ""),
            ("", "", "c", "", ""),
            ("", "", "", "d", ""),
            ("", "", "", "", "e"),
            ("a", "b", "", "", ""),
            ("a", "", "c", "", ""),
            ("a", "", "", "d", ""),
            ("a", "", "", "", "e"),
            ("", "b", "c", "", ""),
            ("", "b", "", "d", ""),
            ("", "b", "", "", "e"),
            ("", "", "c", "d", ""),
            ("", "", "c", "", "e"),
            ("", "", "", "d", "e"),
            ("a", "b", "c", "", ""),
            ("a", "b", "", "d", ""),
            ("a", "b", "", "", "e"),
            # Not all permutations tested, but this should be sufficient
        ],
    )
    @pytest.mark.skip(
        "Reactivate with univention/components/authorization-engine/guardian#98"
    )
    def test_create_db_string_missing_values(
        self, dialect, host, port, db_name, username, password
    ):
        with pytest.raises(
            ValueError,
            match=f"The dialect {dialect} requires a host, db_name, username and password to connect.",
        ):
            SQLAlchemyMixin.create_db_string(
                dialect, host, port, db_name, username, password
            )

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test__get_single_object(self, sqlalchemy_mixin, create_app):
        async with sqlalchemy_mixin.session() as session:
            app = await create_app(session)
        result = await sqlalchemy_mixin._get_single_object(DBApp, name="app")
        assert result.name == app.name
        assert result.display_name == app.display_name
        assert result.id == app.id

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test__get_single_object_multiple_identifier(
        self, sqlalchemy_mixin, create_app, create_namespace
    ):
        async with sqlalchemy_mixin.session() as session:
            app = await create_app(session)
            await session.commit()
            namespace = await create_namespace(session, app_name=app.name)
        result = await sqlalchemy_mixin._get_single_object(
            DBNamespace, name="namespace", app_name=app.name
        )
        assert result.name == namespace.name
        assert result.display_name == namespace.display_name
        assert result.id == namespace.id
        assert result.app_id == app.id

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test__get_single_object_none(
        self, sqlalchemy_mixin, create_app, create_namespace
    ):
        async with sqlalchemy_mixin.session() as session:
            app = await create_app(session)
            await create_namespace(session, app_name=app.name)
        result = await sqlalchemy_mixin._get_single_object(
            DBNamespace, name="namespace2", app_name=app.name
        )
        assert result is None

    @pytest.mark.parametrize("num_apps", [0, 1, 10, 100, 1056])
    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio()
    async def test__get_num_objects(self, sqlalchemy_mixin, create_apps, num_apps):
        async with sqlalchemy_mixin.session() as session:
            apps = await create_apps(session, num_apps)
            counted_num = await sqlalchemy_mixin._get_num_objects(DBApp)
        assert counted_num == len(apps)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
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
    async def test__get_many_objects(
        self, sqlalchemy_mixin, create_namespaces, limit: int | None, offset
    ):
        async with sqlalchemy_mixin.session() as session:
            namespaces = await create_namespaces(session, 10, 10)
            namespaces.sort(key=lambda x: x.name)
        selected_slice = (
            namespaces[offset : offset + limit] if limit else namespaces[offset:]
        )
        result = await sqlalchemy_mixin._get_many_objects(DBNamespace, offset, limit)
        assert [obj.name for obj in result] == [obj.name for obj in selected_slice]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test__get_many_objects_identifiers(
        self, sqlalchemy_mixin, create_permissions
    ):
        async with sqlalchemy_mixin.session() as session:
            permissions = await create_permissions(session, 5, 5, 5)
        namespace_name = permissions[0].namespace.name
        app_name = permissions[0].namespace.app.name
        permissions_beginning = [
            perm
            for perm in permissions
            if perm.namespace.name == namespace_name
            and perm.namespace.app.name == app_name
        ]
        result = await sqlalchemy_mixin._get_many_objects(
            DBPermission, 0, None, app_name=app_name, namespace_name=namespace_name
        )
        assert [perm.id for perm in result] == [
            perm.id for perm in permissions_beginning
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test__get_many_objects_identifiers_namespaces(
        self, sqlalchemy_mixin, create_namespaces
    ):
        async with sqlalchemy_mixin.session() as session:
            namespaces = await create_namespaces(session, 10, 10)
        app_name = namespaces[0].app.name
        namespaces_beginning = [ns for ns in namespaces if ns.app.name == app_name]
        result = await sqlalchemy_mixin._get_many_objects(
            DBNamespace, 0, None, app_name=app_name
        )
        assert [ns.id for ns in result] == [ns.id for ns in namespaces_beginning]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test__get_many_objects_by_app(self, sqlalchemy_mixin, create_roles):
        async with sqlalchemy_mixin.session() as session:
            roles = await create_roles(session, 10, 2, 2)
        app_name = roles[0].namespace.app.name
        roles_beginning = [
            role for role in roles if role.namespace.app.name == app_name
        ]
        roles_beginning.sort(key=lambda x: x.name)
        result = await sqlalchemy_mixin._get_many_objects(
            DBRole, 0, None, app_name=app_name
        )
        result.sort(key=lambda x: x.name)
        assert [role.id for role in result] == [role.id for role in roles_beginning]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test__create_object(self, sqlalchemy_mixin, create_app):
        async with sqlalchemy_mixin.session() as session:
            app = await create_app(session)
            ns = DBNamespace(app_id=app.id, name="ns", display_name="NS")
            await sqlalchemy_mixin._create_object(ns)
            async with session.begin():
                found = (await session.scalars(select(DBNamespace))).one()
                assert found.app_id == app.id
                assert found.name == ns.name
                assert found.display_name == ns.display_name

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test__create_object_exists_error(self, sqlalchemy_mixin, create_app):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, name="app")
            with pytest.raises(
                ObjectExistsError,
                match="An object with the given identifiers already exists.",
            ):
                await sqlalchemy_mixin._create_object(
                    DBApp(name="app", display_name="FOO")
                )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test__create_object_parent_not_found(self, sqlalchemy_mixin, create_app):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            ns = DBNamespace(app_id=2, name="ns", display_name="NS")
            with pytest.raises(
                ParentNotFoundError,
                match="The app/namespace of the object to be created does not exist.",
            ):
                await sqlalchemy_mixin._create_object(ns)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test__update_object(self, sqlalchemy_mixin, create_app):
        async with sqlalchemy_mixin.session() as session:
            app = await create_app(session, display_name="App")
        result = await sqlalchemy_mixin._update_object(app, display_name="FOO")
        assert result.display_name == "FOO"
