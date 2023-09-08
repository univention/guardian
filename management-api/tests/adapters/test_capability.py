# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from copy import deepcopy

import pytest
import pytest_asyncio
from guardian_management_api.adapters.capability import SQLCapabilityPersistenceAdapter
from guardian_management_api.adapters.permission import SQLPermissionPersistenceAdapter
from guardian_management_api.errors import ObjectNotFoundError, ParentNotFoundError
from guardian_management_api.models.base import PaginationRequest
from guardian_management_api.models.capability import (
    CapabilitiesByRoleQuery,
    CapabilitiesGetQuery,
    Capability,
    CapabilityConditionRelation,
    CapabilityGetQuery,
    ParametrizedCondition,
)
from guardian_management_api.models.permission import Permission
from guardian_management_api.models.role import Role
from guardian_management_api.models.sql_persistence import (
    DBCapability,
    DBCapabilityCondition,
    DBPermission,
    capability_permission_table,
)
from guardian_management_api.ports.capability import CapabilityPersistencePort
from sqlalchemy import select
from sqlalchemy.sql.functions import count


class TestSQLCapabilityPersistenceAdapter:
    @pytest_asyncio.fixture
    async def adapter(self, register_test_adapters) -> SQLCapabilityPersistenceAdapter:
        return await register_test_adapters.request_port(CapabilityPersistencePort)

    @pytest_asyncio.fixture
    async def capability_for_testing(
        self, create_permissions, create_condition, create_role, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_permissions = await create_permissions(session, 2)
            db_cond = await create_condition(
                session,
                db_permissions[0].namespace.app.name,
                db_permissions[0].namespace.name,
            )
            db_role = await create_role(
                session,
                db_permissions[0].namespace.app.name,
                db_permissions[0].namespace.name,
            )
            cap = Capability(
                app_name=db_permissions[0].namespace.app.name,
                namespace_name=db_permissions[0].namespace.name,
                name="cap",
                display_name=None,
                role=Role(
                    app_name=db_role.namespace.app.name,
                    namespace_name=db_role.namespace.name,
                    name=db_role.name,
                ),
                permissions=[
                    Permission(
                        app_name=perm.namespace.app.name,
                        namespace_name=perm.namespace.name,
                        name=perm.name,
                    )
                    for perm in db_permissions
                ],
                relation=CapabilityConditionRelation.AND,
                conditions=[
                    ParametrizedCondition(
                        app_name=db_cond.namespace.app.name,
                        namespace_name=db_cond.namespace.name,
                        name=db_cond.name,
                        parameters={"A": 1, "B": True},
                    )
                ],
            )
            return cap, db_permissions, db_cond, db_role

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test__get_db_children_for_capability(
        self, adapter: SQLCapabilityPersistenceAdapter, create_permissions
    ):
        async with adapter.session() as session:
            db_permissions = await create_permissions(session, 5, 3, 3)
            permissions = [
                SQLPermissionPersistenceAdapter._db_permission_to_permission(
                    db_permission
                )
                for db_permission in (
                    db_permissions[0],
                    db_permissions[-1],
                    db_permissions[4],
                )
            ]
            result = await adapter._get_db_child_objs_for_capability(
                DBPermission, permissions, session=session
            )
            assert result == [
                db_permissions[0],
                db_permissions[4],
                db_permissions[-1],
            ], result

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test__get_db_children_for_capability_not_found_error(
        self, adapter: SQLCapabilityPersistenceAdapter, create_permissions
    ):
        async with adapter.session() as session:
            db_permissions = await create_permissions(session, 5, 3, 3)
            permissions = [
                SQLPermissionPersistenceAdapter._db_permission_to_permission(
                    db_permission
                )
                for db_permission in (
                    db_permissions[0],
                    db_permissions[4],
                    db_permissions[-1],
                )
            ]
            permissions.append(Permission(app_name="a", namespace_name="b", name="c"))
            with pytest.raises(
                ObjectNotFoundError,
                match="Not all permissions specified for the capability could be found.",
            ) as exc_info:
                await adapter._get_db_child_objs_for_capability(
                    DBPermission, permissions, session=session
                )
                assert exc_info.value.object_type == Permission

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create(
        self, adapter: SQLCapabilityPersistenceAdapter, capability_for_testing
    ):
        cap, db_permissions, db_cond, db_role = capability_for_testing
        result = await adapter.create(cap)
        result.permissions.sort(
            key=lambda x: f"{x.app_name}:{x.namespace_name}:{x.name}"
        )
        cap.permissions.sort(key=lambda x: f"{x.app_name}:{x.namespace_name}:{x.name}")
        result.conditions.sort(
            key=lambda x: f"{x.app_name}:{x.namespace_name}:{x.name}"
        )
        cap.conditions.sort(key=lambda x: f"{x.app_name}:{x.namespace_name}:{x.name}")
        assert result == cap
        async with adapter.session() as session:
            db_cap = (
                await session.execute(
                    select(DBCapability).where(DBCapability.name == "cap")
                )
            ).scalar()
        assert db_cap.name == "cap"
        assert {perm.id for perm in db_cap.permissions} == {
            perm.id for perm in db_permissions
        }
        assert db_cap.conditions.pop().condition_id == db_cond.id

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_namespace_not_found(
        self, adapter: SQLCapabilityPersistenceAdapter, capability_for_testing
    ):
        cap, db_permissions, db_cond, db_role = capability_for_testing
        cap.namespace_name = "foo"
        with pytest.raises(
            ParentNotFoundError,
            match="The namespace of the capability to create does not exist.",
        ):
            await adapter.create(cap)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_role_not_found(
        self, adapter: SQLCapabilityPersistenceAdapter, capability_for_testing
    ):
        cap, db_permissions, db_cond, db_role = capability_for_testing
        cap.role.name = "foo"
        with pytest.raises(
            ObjectNotFoundError, match="The capabilities role could not be found."
        ) as exc_info:
            await adapter.create(cap)
        assert exc_info.value.object_type == Role

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one(
        self, adapter: SQLCapabilityPersistenceAdapter, capability_for_testing
    ):
        cap, db_permissions, db_cond, db_role = capability_for_testing
        await adapter.create(cap)
        result = await adapter.read_one(
            CapabilityGetQuery(
                app_name=cap.app_name, namespace_name=cap.namespace_name, name=cap.name
            )
        )
        result.permissions.sort(
            key=lambda x: f"{x.app_name}:{x.namespace_name}:{x.name}"
        )
        cap.permissions.sort(key=lambda x: f"{x.app_name}:{x.namespace_name}:{x.name}")
        result.conditions.sort(
            key=lambda x: f"{x.app_name}:{x.namespace_name}:{x.name}"
        )
        cap.conditions.sort(key=lambda x: f"{x.app_name}:{x.namespace_name}:{x.name}")
        assert result == cap

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_one_not_found_error(
        self, adapter: SQLCapabilityPersistenceAdapter, capability_for_testing
    ):
        cap, db_permissions, db_cond, db_role = capability_for_testing
        await adapter.create(cap)
        with pytest.raises(
            ObjectNotFoundError,
            match=f"No capability with the identifier "
            f"'{cap.app_name}:{cap.namespace_name}:foo' could be found.",
        ):
            await adapter.read_one(
                CapabilityGetQuery(
                    app_name=cap.app_name, namespace_name=cap.namespace_name, name="foo"
                )
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete(
        self, adapter: SQLCapabilityPersistenceAdapter, create_capabilities
    ):
        async with adapter.session() as session:
            db_cap = (await create_capabilities(session, 1))[0]
            cap = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        assert (
            await adapter.delete(
                CapabilityGetQuery(
                    app_name=cap.app_name,
                    namespace_name=cap.namespace_name,
                    name=cap.name,
                )
            )
            is None
        )
        async with adapter.session() as session:
            obj = (await session.execute(select(DBCapability))).scalar()
            cap_cond_count = (
                await session.execute(select(count(DBCapabilityCondition.id)))
            ).scalar()
            cap_perms = (
                await session.execute(select(capability_permission_table))
            ).all()
        assert obj is None
        assert cap_cond_count == 0
        assert len(cap_perms) == 0

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_not_found_error(
        self, adapter: SQLCapabilityPersistenceAdapter, capability_for_testing
    ):
        cap, db_permissions, db_cond, db_role = capability_for_testing
        result = await adapter.create(cap)
        async with adapter.session() as session:
            obj = (await session.execute(select(DBCapability))).scalar()
        assert obj.name == result.name  # Just make sure the obj is in the database
        cap.name = "foo"
        with pytest.raises(ObjectNotFoundError) as exc_info:
            await adapter.delete(cap)
        assert exc_info.value.object_type == Capability

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update(
        self, adapter: SQLCapabilityPersistenceAdapter, capability_for_testing
    ):
        cap, db_permissions, db_cond, db_role = capability_for_testing
        await adapter.create(cap)
        cap2 = deepcopy(cap)
        cap2.display_name = "FOO"
        cap2.permissions = []
        result = await adapter.update(cap2)
        assert result.display_name == "FOO"
        assert result.name == cap.name
        assert result.role == cap.role
        assert result.permissions == []
        async with adapter.session() as session:
            db_cap = (await session.execute(select(DBCapability))).unique().scalar_one()
        assert db_cap.display_name == "FOO"
        assert db_cap.role.name == cap.role.name
        assert db_cap.permissions == set()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update_not_found(
        self, adapter: SQLCapabilityPersistenceAdapter, capability_for_testing
    ):
        cap, db_permissions, db_cond, db_role = capability_for_testing
        await adapter.create(cap)
        cap.name = "FOO"
        with pytest.raises(
            ObjectNotFoundError,
            match=f"No capability with the identifier "
            f"'{cap.app_name}:{cap.namespace_name}:{cap.name}' could be found.",
        ):
            await adapter.delete(cap)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_many_empty(self, adapter: SQLCapabilityPersistenceAdapter):
        result = await adapter.read_many(
            CapabilitiesGetQuery(
                pagination=PaginationRequest(query_limit=None, query_offset=0)
            )
        )
        assert result.total_count == 0
        assert result.objects == []

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
        adapter: SQLCapabilityPersistenceAdapter,
        create_capabilities,
        limit,
        offset,
    ):
        async with adapter.session() as session:
            db_capabilities = await create_capabilities(session, 100)
            db_capabilities.sort(key=lambda x: x.name)
        result = await adapter.read_many(
            CapabilitiesGetQuery(
                pagination=PaginationRequest(query_offset=offset, query_limit=limit)
            )
        )
        selected_slice = (
            db_capabilities[offset : offset + limit]
            if limit
            else db_capabilities[offset:]
        )
        assert result.total_count == 100
        assert [obj.name for obj in result.objects] == [
            obj.name for obj in selected_slice
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_many_by_role(
        self, adapter: SQLCapabilityPersistenceAdapter, create_capabilities
    ):
        async with adapter.session() as session:
            db_capabilities = await create_capabilities(session, 10, 5)
            app_name = db_capabilities[0].role.namespace.app.name
            namespace_name = db_capabilities[0].role.namespace.name
            role_name = db_capabilities[0].role.name
        result = await adapter.read_many(
            CapabilitiesByRoleQuery(
                pagination=PaginationRequest(query_limit=5, query_offset=0),
                app_name=app_name,
                namespace_name=namespace_name,
                role_name=role_name,
            )
        )
        assert len(list(result.objects)) == 5
        assert result.total_count == 10
        assert [obj.name for obj in result.objects] == [
            obj.name for obj in db_capabilities
        ][:5]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_read_many_wrong_query_type(
        self, adapter: SQLCapabilityPersistenceAdapter
    ):
        with pytest.raises(RuntimeError, match="Unknown query type."):
            await adapter.read_many(True)
