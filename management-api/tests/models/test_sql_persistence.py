import pytest
from guardian_management_api.models.capability import CapabilityConditionRelation
from guardian_management_api.models.condition import ConditionParameterType
from guardian_management_api.models.sql_persistence import (
    DBApp,
    DBCapability,
    DBCapabilityCondition,
    DBCondition,
    DBConditionParameter,
    DBNamespace,
    DBPermission,
    DBRole,
    capability_permission_table,
)
from sqlalchemy import select


@pytest.mark.asyncio
@pytest.mark.usefixtures("create_tables")
async def test_cap_permission_cascading(sqlalchemy_mixin):
    """
    Tests that if a capability is deleted, that the association to its permissions was deleted;
    but not the permission itself.
    """
    async with sqlalchemy_mixin.session() as session:
        async with session.begin():
            db_app = DBApp(name="app1")
            db_ns = DBNamespace(app=db_app, name="ns1")
            db_perm = DBPermission(namespace=db_ns, name="p1")
            db_role = DBRole(namespace=db_ns, name="role1")
            db_cap = DBCapability(
                namespace=db_ns,
                name="test",
                permissions={db_perm},
                role=db_role,
                conditions=set(),
                relation=CapabilityConditionRelation.AND,
            )
            session.add_all([db_app, db_ns, db_perm, db_role, db_cap])
        async with session.begin():
            await session.delete(db_cap)
        result = (await session.execute(select(DBPermission.name))).scalars()
        assert list(result) == ["p1"]
        result = (await session.execute(select(capability_permission_table))).scalars()
        assert list(result) == []


@pytest.mark.asyncio
@pytest.mark.usefixtures("create_tables")
async def test_permission_cap_cascading(sqlalchemy_mixin):
    """
    Tests that if a permission is deleted, that the association to a capability was deleted;
    but not the capability
    """
    async with sqlalchemy_mixin.session() as session:
        async with session.begin():
            db_app = DBApp(name="app1")
            db_ns = DBNamespace(app=db_app, name="ns1")
            db_perm = DBPermission(namespace=db_ns, name="p1")
            db_role = DBRole(namespace=db_ns, name="role1")
            db_cap = DBCapability(
                namespace=db_ns,
                name="test",
                permissions={db_perm},
                role=db_role,
                conditions=set(),
                relation=CapabilityConditionRelation.AND,
            )
            session.add_all([db_app, db_ns, db_perm, db_role, db_cap])
        async with session.begin():
            await session.delete(db_perm)
        result = (await session.execute(select(DBPermission.name))).scalars()
        assert list(result) == []
        result = (await session.execute(select(capability_permission_table))).scalars()
        assert list(result) == []
        result = (await session.execute(select(DBCapability.name))).scalars()
        assert list(result) == ["test"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("create_tables")
async def test_cap_condition_cascading(sqlalchemy_mixin):
    """
    Tests that if a capability is deleted, that the association to its conditions was deleted;
    but not the condition itself.
    """
    async with sqlalchemy_mixin.session() as session:
        async with session.begin():
            db_app = DBApp(name="app1")
            db_ns = DBNamespace(app=db_app, name="ns1")
            db_role = DBRole(namespace=db_ns, name="role1")
            db_cond = DBCondition(
                namespace=db_ns, name="cond1", parameters=[], code=b""
            )
            db_cap = DBCapability(
                namespace=db_ns,
                name="test",
                permissions=set(),
                role=db_role,
                conditions={DBCapabilityCondition(condition=db_cond, kwargs={})},
                relation=CapabilityConditionRelation.AND,
            )
            session.add_all([db_app, db_ns, db_role, db_cond, db_cap])
        async with session.begin():
            await session.delete(db_cap)
        result = (await session.execute(select(DBCondition.name))).scalars()
        assert list(result) == ["cond1"]
        result = (await session.execute(select(DBCapabilityCondition))).scalars()
        assert list(result) == []


@pytest.mark.asyncio
@pytest.mark.usefixtures("create_tables")
async def test_condition_cap_cascading(sqlalchemy_mixin):
    """
    Tests that if a condition is deleted, that the association to its capabilities was deleted;
    but not the capability itself.
    """
    async with sqlalchemy_mixin.session() as session:
        async with session.begin():
            db_app = DBApp(name="app1")
            db_ns = DBNamespace(app=db_app, name="ns1")
            db_role = DBRole(namespace=db_ns, name="role1")
            db_cond = DBCondition(
                namespace=db_ns, name="cond1", parameters=[], code=b""
            )
            db_cap = DBCapability(
                namespace=db_ns,
                name="test",
                permissions=set(),
                role=db_role,
                conditions={DBCapabilityCondition(condition=db_cond, kwargs={})},
                relation=CapabilityConditionRelation.AND,
            )
            session.add_all([db_app, db_ns, db_role, db_cond, db_cap])
        async with session.begin():
            await session.delete(db_cond)
        result = (await session.execute(select(DBCondition.name))).scalars()
        assert list(result) == []
        result = (await session.execute(select(DBCapabilityCondition))).scalars()
        assert list(result) == []
        result = (await session.execute(select(DBCapability.name))).scalars()
        assert list(result) == ["test"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("create_tables")
async def test_condition_parameter_cascading(sqlalchemy_mixin):
    """
    Tests that if a condition is deleted or a parameter removed from the condition,
    that its parameters are deleted as well.
    """
    async with sqlalchemy_mixin.session() as session:
        async with session.begin():
            db_app = DBApp(name="app1")
            db_ns = DBNamespace(app=db_app, name="ns1")
            db_param = DBConditionParameter(
                name="param1", value_type=ConditionParameterType.ANY, position=0
            )
            db_param2 = DBConditionParameter(
                name="param2", value_type=ConditionParameterType.ANY, position=1
            )
            db_cond = DBCondition(
                namespace=db_ns,
                name="cond1",
                parameters=[db_param, db_param2],
                code=b"",
            )
            session.add_all([db_app, db_ns, db_cond])
        async with session.begin():
            db_cond.parameters = [db_param2]
            session.add(db_cond)
        async with session.begin():
            result = (
                await session.execute(select(DBConditionParameter.name))
            ).scalars()
        assert list(result) == ["param2"]
        async with session.begin():
            await session.delete(db_cond)
        result = (await session.execute(select(DBCondition.name))).scalars()
        assert list(result) == []
        result = (await session.execute(select(DBConditionParameter))).scalars()
        assert list(result) == []


@pytest.mark.asyncio
@pytest.mark.usefixtures("create_tables")
async def test_parameter_condition_cascading(sqlalchemy_mixin):
    """
    Tests that if a parameter is deleted, that its condition is not deleted.
    """
    async with sqlalchemy_mixin.session() as session:
        async with session.begin():
            db_app = DBApp(name="app1")
            db_ns = DBNamespace(app=db_app, name="ns1")
            db_param = DBConditionParameter(
                name="param1", value_type=ConditionParameterType.ANY, position=0
            )
            db_cond = DBCondition(
                namespace=db_ns, name="cond1", parameters=[db_param], code=b""
            )
            session.add_all([db_app, db_ns, db_cond])
        async with session.begin():
            await session.delete(db_param)
        result = (await session.execute(select(DBCondition.name))).scalars()
        assert list(result) == ["cond1"]
        result = (await session.execute(select(DBConditionParameter))).scalars()
        assert list(result) == []
