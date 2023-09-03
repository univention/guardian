# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
import pytest_asyncio
from guardian_management_api.adapters.condition import SQLConditionPersistenceAdapter
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
from guardian_management_api.models.condition import (
    Condition,
    ConditionGetQuery,
    ConditionsGetQuery,
)
from guardian_management_api.models.sql_persistence import (
    DBCondition,
    SQLPersistenceAdapterSettings,
)
from sqlalchemy import select


class TestSQLConditionPersistenceAdapter:
    @pytest_asyncio.fixture
    async def condition_sql_adapter(self, sqlite_url) -> SQLConditionPersistenceAdapter:
        adapter = SQLConditionPersistenceAdapter()
        await adapter.configure(
            SQLPersistenceAdapterSettings(dialect="sqlite", db_name=sqlite_url)
        )
        return adapter

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create(
        self, condition_sql_adapter: SQLConditionPersistenceAdapter, create_namespaces
    ):
        async with condition_sql_adapter.session() as session:
            namespace = (await create_namespaces(session, 1))[0]
        condition = await condition_sql_adapter.create(
            Condition(
                app_name=namespace.app.name,
                namespace_name=namespace.name,
                name="condition",
                display_name="Condition",
                documentation="doc",
                parameters=["a", "b", "c"],
                code=b"CODE",
            )
        )
        assert condition == Condition(
            app_name=namespace.app.name,
            namespace_name=namespace.name,
            name="condition",
            display_name="Condition",
            documentation="doc",
            parameters=["a", "b", "c"],
            code=b"CODE",
        )
        async with condition_sql_adapter.session() as session:
            result = (await session.scalars(select(DBCondition))).one()
            assert result.namespace_id == namespace.id
            assert result.name == "condition"
            assert result.display_name == "Condition"
            assert result.documentation == "doc"
            assert result.parameters == "a,b,c"
            assert result.code == b"CODE"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_exists_error(
        self,
        condition_sql_adapter: SQLConditionPersistenceAdapter,
        create_condition,
        create_namespaces,
    ):
        async with condition_sql_adapter.session() as session:
            namespace = (await create_namespaces(session, 1))[0]
            condition = await create_condition(
                session, app_name=namespace.app.name, namespace_name=namespace.name
            )
        with pytest.raises(ObjectExistsError):
            await condition_sql_adapter.create(
                Condition(
                    app_name=condition.namespace.app.name,
                    namespace_name=condition.namespace.name,
                    name=condition.name,
                    display_name="Condition",
                    code=b"CODE",
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_app_not_found_error(
        self,
        condition_sql_adapter: SQLConditionPersistenceAdapter,
    ):
        with pytest.raises(
            ParentNotFoundError,
            match="The app of the object to be created does not exist.",
        ):
            await condition_sql_adapter.create(
                Condition(
                    app_name="app",
                    namespace_name="namespace",
                    name="condition",
                    display_name="Condition",
                    code=b"CODE",
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_namespace_not_found_error(
        self, condition_sql_adapter: SQLConditionPersistenceAdapter, create_apps
    ):
        async with condition_sql_adapter.session() as session:
            app = (await create_apps(session, 1))[0]
        with pytest.raises(
            ParentNotFoundError,
            match="The namespace of the object to be created does not exist.",
        ):
            await condition_sql_adapter.create(
                Condition(
                    app_name=app.name,
                    namespace_name="namespace",
                    name="condition",
                    display_name="Condition",
                    code=b"CODE",
                )
            )

    @pytest.mark.asyncio
    async def test_create_unhandled_error(
        self, condition_sql_adapter: SQLConditionPersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await condition_sql_adapter.create(
                Condition(
                    app_name="foo",
                    namespace_name="bar",
                    name="condition",
                    display_name="Condition",
                    code=b"CODE",
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one(
        self,
        condition_sql_adapter: SQLConditionPersistenceAdapter,
        create_conditions,
    ):
        async with condition_sql_adapter.session() as session:
            db_condition = (await create_conditions(session, 1))[0]
        condition = await condition_sql_adapter.read_one(
            ConditionGetQuery(
                app_name=db_condition.namespace.app.name,
                namespace_name=db_condition.namespace.name,
                name=db_condition.name,
            )
        )
        assert condition.app_name == db_condition.namespace.app.name
        assert condition.namespace_name == db_condition.namespace.name
        assert condition.name == db_condition.name
        assert condition.display_name == db_condition.display_name

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one_none(
        self,
        condition_sql_adapter: SQLConditionPersistenceAdapter,
    ):
        with pytest.raises(ObjectNotFoundError):
            await condition_sql_adapter.read_one(
                ConditionGetQuery(
                    app_name="foo", namespace_name="bar", name="condition"
                )
            )

    @pytest.mark.asyncio
    async def test_read_one_unhandled_error(
        self, condition_sql_adapter: SQLConditionPersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await condition_sql_adapter.read_one(
                ConditionGetQuery(
                    app_name="foo", namespace_name="bar", name="condition"
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_many_empty(
        self, condition_sql_adapter: SQLConditionPersistenceAdapter
    ):
        result = await condition_sql_adapter.read_many(
            ConditionsGetQuery(pagination=PaginationRequest(query_offset=0))
        )
        assert result == PersistenceGetManyResult(total_count=0, objects=[])

    @pytest.mark.asyncio
    async def test_read_many_unhandled_error(
        self, condition_sql_adapter: SQLConditionPersistenceAdapter
    ):
        with pytest.raises(PersistenceError):
            await condition_sql_adapter.read_many(
                ConditionsGetQuery(pagination=PaginationRequest(query_offset=0))
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
        condition_sql_adapter: SQLConditionPersistenceAdapter,
        create_conditions,
        limit,
        offset,
    ):
        async with condition_sql_adapter.session() as session:
            conditions = await create_conditions(session, 5, 2, 10)
            conditions.sort(key=lambda x: x.name)
        result = await condition_sql_adapter.read_many(
            ConditionsGetQuery(
                pagination=PaginationRequest(query_offset=offset, query_limit=limit)
            )
        )
        selected_slice = (
            conditions[offset : offset + limit] if limit else conditions[offset:]
        )
        assert result.total_count == 100
        assert [obj.name for obj in result.objects] == [
            obj.name for obj in selected_slice
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update(
        self,
        condition_sql_adapter: SQLConditionPersistenceAdapter,
        create_conditions,
    ):
        async with condition_sql_adapter.session() as session:
            db_condition = (await create_conditions(session, 1))[0]
        result = await condition_sql_adapter.update(
            Condition(
                app_name=db_condition.namespace.app.name,
                namespace_name=db_condition.namespace.name,
                name=db_condition.name,
                display_name="NEW DISPLAY NAME",
                documentation="NEW DOC",
                parameters=["N", "E", "W"],
                code=b"NEW CODE",
            )
        )
        assert result == Condition(
            app_name=db_condition.namespace.app.name,
            namespace_name=db_condition.namespace.name,
            name=db_condition.name,
            display_name="NEW DISPLAY NAME",
            documentation="NEW DOC",
            parameters=["N", "E", "W"],
            code=b"NEW CODE",
        )
        async with condition_sql_adapter.session() as session:
            result = (await session.scalars(select(DBCondition))).one()
            assert result.name == db_condition.name
            assert result.display_name == "NEW DISPLAY NAME"
            assert result.documentation == "NEW DOC"
            assert result.parameters == "N,E,W"
            assert result.code == b"NEW CODE"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update_object_not_found_error(
        self,
        condition_sql_adapter: SQLConditionPersistenceAdapter,
        create_conditions,
    ):
        async with condition_sql_adapter.session() as session:
            await create_conditions(session, 1)
        with pytest.raises(
            ObjectNotFoundError,
            match="No condition with the identifier 'app:namespace:condition' could be found.",
        ):
            await condition_sql_adapter.update(
                Condition(
                    app_name="app",
                    namespace_name="namespace",
                    name="condition",
                    display_name="NEW DISPLAY NAME",
                    code=b"CODE",
                )
            )
