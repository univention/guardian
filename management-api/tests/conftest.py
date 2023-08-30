# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import os
from base64 import b64encode
from typing import Optional

import guardian_lib.adapter_registry as adapter_registry
import pytest
import pytest_asyncio
from guardian_lib.ports import SettingsPort
from guardian_management_api.adapters.app import (
    AppStaticDataAdapter,
    FastAPIAppAPIAdapter,
)
from guardian_management_api.models.sql_persistence import (
    Base,
    DBApp,
    DBCondition,
    DBContext,
    DBNamespace,
    DBPermission,
    DBRole,
)
from guardian_management_api.ports.app import (
    AppAPIPort,
    AppPersistencePort,
)
from port_loader import AsyncAdapterRegistry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


class DummySettingsAdapter(SettingsPort):
    """Dummy settings adapter."""

    class Config:
        alias = "dummy"

    async def get_int(self, setting_name: str, default: Optional[int] = None) -> int:
        return 0

    async def get_str(self, setting_name: str, default: Optional[str] = None) -> str:
        return ""

    async def get_bool(self, setting_name: str, default: Optional[bool] = None) -> bool:
        return False


@pytest.fixture()
def register_test_adapters():
    """Fixture that registers the test adapters.

    In this case:
      - In-memory app persistence adapter.
      - Dummy settings adapter.
    """
    _environ = os.environ.copy()
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__APP_PERSISTENCE_PORT"] = "in_memory"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__SETTINGS_PORT"] = "dummy"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__APP_API_PORT"] = "APP_API_PORT"
    adapter_registry.ADAPTER_REGISTRY.register_port(SettingsPort)
    adapter_registry.ADAPTER_REGISTRY.register_adapter(
        SettingsPort,
        adapter_cls=DummySettingsAdapter,
    )
    adapter_registry.ADAPTER_REGISTRY.set_adapter(
        SettingsPort,
        DummySettingsAdapter,
    )
    adapter_registry.ADAPTER_REGISTRY.register_port(AppPersistencePort)
    adapter_registry.ADAPTER_REGISTRY.register_adapter(
        AppPersistencePort,
        adapter_cls=AppStaticDataAdapter,
    )
    adapter_registry.ADAPTER_REGISTRY.set_adapter(
        AppPersistencePort,
        AppStaticDataAdapter,
    )
    adapter_registry.ADAPTER_REGISTRY.register_port(AppAPIPort)
    adapter_registry.ADAPTER_REGISTRY.register_adapter(
        AppAPIPort,
        adapter_cls=FastAPIAppAPIAdapter,
    )
    adapter_registry.ADAPTER_REGISTRY.set_adapter(
        AppAPIPort,
        FastAPIAppAPIAdapter,
    )

    yield adapter_registry.ADAPTER_REGISTRY
    os.environ.clear()
    os.environ.update(_environ)
    adapter_registry.ADAPTER_REGISTRY = AsyncAdapterRegistry()


@pytest.fixture
def sqlite_url(tmpdir):
    return f"///{tmpdir / 'management.db'}"


@pytest_asyncio.fixture
async def create_tables(sqlite_url):
    engine = create_async_engine(f"sqlite+aiosqlite:{sqlite_url}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
def create_app():
    async def _create_app(
        session: AsyncSession, name: str = "app", display_name: str = "App"
    ) -> DBApp:
        async with session.begin():
            app = DBApp(name=name, display_name=display_name)
            session.add(app)
        return app

    return _create_app


@pytest.fixture
def create_apps(create_app):
    async def _create_apps(session: AsyncSession, num_apps: int) -> list[DBApp]:
        async with session.begin():
            apps = [
                DBApp(name=f"app_{i:09d}", display_name=f"App {i}")
                for i in range(num_apps)
            ]
            session.add_all(apps)
        return apps

    return _create_apps


@pytest.fixture
def create_namespace():
    async def _create_namespace(
        session: AsyncSession,
        app_name: str = "app",
        name: str = "namespace",
        display_name: str = "Namespace",
    ):
        async with session.begin():
            app = (
                await session.execute(select(DBApp).where(DBApp.name == app_name))
            ).scalar()
        async with session.begin():
            namespace = DBNamespace(name=name, display_name=display_name, app_id=app.id)
            session.add(namespace)
        return namespace

    return _create_namespace


@pytest.fixture
def create_namespaces(create_namespace, create_apps):
    async def _create_namespaces(
        session: AsyncSession, namespaces_per_app: int, num_apps: int = 1
    ) -> list[DBNamespace]:
        apps = await create_apps(session, num_apps)
        async with session.begin():
            namespaces = [
                DBNamespace(
                    app_id=app.id,
                    name=f"namespace_{app.id:09d}_{i:09d}",
                    display_name=f"Namespace {app.id} {i}",
                )
                for i in range(namespaces_per_app)
                for app in apps
            ]
            session.add_all(namespaces)
        async with session.begin():
            [
                await session.refresh(namespace, attribute_names=["app"])
                for namespace in namespaces
            ]
        return namespaces

    return _create_namespaces


@pytest.fixture
def create_permission():
    async def _create_permission(
        session: AsyncSession,
        app_name: str = "app",
        namespace_name: str = "namespace",
        name: str = "permission",
        display_name: str = "Permission",
    ):
        async with session.begin():
            app = (
                await session.execute(select(DBApp).where(DBApp.name == app_name))
            ).scalar()
            namespace = (
                await session.execute(
                    select(DBNamespace).where(
                        DBNamespace.app_id == app.id, DBNamespace.name == namespace_name
                    )
                )
            ).scalar()
        async with session.begin():
            permission = DBPermission(
                namespace_id=namespace.id, name=name, display_name=display_name
            )
            session.add(permission)
        async with session.begin():
            await session.refresh(permission, attribute_names=["namespace"])
        return permission

    return _create_permission


@pytest.fixture
def create_permissions(create_namespaces):
    async def _create_permissions(
        session: AsyncSession,
        permissions_per_namespace: int,
        namespaces_per_app: int = 1,
        num_apps: int = 1,
    ) -> list[DBPermission]:
        namespaces = await create_namespaces(session, namespaces_per_app, num_apps)
        async with session.begin():
            permissions = [
                DBPermission(
                    namespace_id=namespace.id,
                    name=f"permission_{namespace.app_id:09d}_{namespace.id:09d}_{i:09d}",
                    display_name=f"Permission {namespace.app_id} {namespace.id} {i}",
                )
                for i in range(permissions_per_namespace)
                for namespace in namespaces
            ]
            session.add_all(permissions)
        async with session.begin():
            [
                await session.refresh(permission, attribute_names=["namespace"])
                for permission in permissions
            ]
        return permissions

    return _create_permissions


@pytest.fixture
def create_role():
    async def _create_role(
        session: AsyncSession,
        app_name: str = "app",
        namespace_name: str = "namespace",
        name: str = "role",
        display_name: str = "Role",
    ):
        async with session.begin():
            app = (
                await session.execute(select(DBApp).where(DBApp.name == app_name))
            ).scalar()
            namespace = (
                await session.execute(
                    select(DBNamespace).where(
                        DBNamespace.app_id == app.id, DBNamespace.name == namespace_name
                    )
                )
            ).scalar()
        async with session.begin():
            role = DBRole(
                namespace_id=namespace.id, name=name, display_name=display_name
            )
            session.add(role)
        async with session.begin():
            await session.refresh(role, attribute_names=["namespace"])
        return role

    return _create_role


@pytest.fixture
def create_roles(create_namespaces):
    async def _create_roles(
        session: AsyncSession,
        roles_per_namespace: int,
        namespaces_per_app: int = 1,
        num_apps: int = 1,
    ) -> list[DBRole]:
        namespaces = await create_namespaces(session, namespaces_per_app, num_apps)
        async with session.begin():
            roles = [
                DBRole(
                    namespace_id=namespace.id,
                    name=f"role_{namespace.app_id:09d}_{namespace.id:09d}_{i:09d}",
                    display_name=f"Role {namespace.app_id} {namespace.id} {i}",
                )
                for i in range(roles_per_namespace)
                for namespace in namespaces
            ]
            session.add_all(roles)
        async with session.begin():
            [
                await session.refresh(role, attribute_names=["namespace"])
                for role in roles
            ]
        return roles

    return _create_roles


@pytest.fixture
def create_context():
    async def _create_context(
        session: AsyncSession,
        app_name: str = "app",
        namespace_name: str = "namespace",
        name: str = "context",
        display_name: str = "Context",
    ):
        async with session.begin():
            app = (
                await session.execute(select(DBApp).where(DBApp.name == app_name))
            ).scalar()
            namespace = (
                await session.execute(
                    select(DBNamespace).where(
                        DBNamespace.app_id == app.id, DBNamespace.name == namespace_name
                    )
                )
            ).scalar()
        async with session.begin():
            context = DBContext(
                namespace_id=namespace.id, name=name, display_name=display_name
            )
            session.add(context)
        async with session.begin():
            await session.refresh(context, attribute_names=["namespace"])
        return context

    return _create_context


@pytest.fixture
def create_contexts(create_namespaces):
    async def _create_contexts(
        session: AsyncSession,
        contexts_per_namespace: int,
        namespaces_per_app: int = 1,
        num_apps: int = 1,
    ) -> list[DBContext]:
        namespaces = await create_namespaces(session, namespaces_per_app, num_apps)
        async with session.begin():
            contexts = [
                DBContext(
                    namespace_id=namespace.id,
                    name=f"context_{namespace.app_id:09d}_{namespace.id:09d}_{i:09d}",
                    display_name=f"Context {namespace.app_id} {namespace.id} {i}",
                )
                for i in range(contexts_per_namespace)
                for namespace in namespaces
            ]
            session.add_all(contexts)
        async with session.begin():
            [
                await session.refresh(context, attribute_names=["namespace"])
                for context in contexts
            ]
        return contexts

    return _create_contexts


@pytest.fixture
def create_condition():
    async def _create_condition(
        session: AsyncSession,
        app_name: str = "app",
        namespace_name: str = "namespace",
        name: str = "condition",
        display_name: str = "Condition",
        documentation: str = "docstring",
        parameters: Optional[list[str]] = None,
        code: Optional[bytes] = None,
    ):
        if parameters is None:
            parameters = ["a", "b"]
        if code is None:
            code = b64encode(b"CODE")
        async with session.begin():
            app = (
                await session.execute(select(DBApp).where(DBApp.name == app_name))
            ).scalar()
            namespace = (
                await session.execute(
                    select(DBNamespace).where(
                        DBNamespace.app_id == app.id, DBNamespace.name == namespace_name
                    )
                )
            ).scalar()
        async with session.begin():
            condition = DBCondition(
                namespace_id=namespace.id,
                name=name,
                display_name=display_name,
                documentation=documentation,
                parameters=",".join(parameters),
                code=code,
            )
            session.add(condition)
        async with session.begin():
            await session.refresh(condition, attribute_names=["namespace"])
        return condition

    return _create_condition


@pytest.fixture
def create_conditions(create_namespaces):
    async def _create_conditions(
        session: AsyncSession,
        conditions_per_namespace: int,
        namespaces_per_app: int = 1,
        num_apps: int = 1,
    ) -> list[DBCondition]:
        namespaces = await create_namespaces(session, namespaces_per_app, num_apps)
        async with session.begin():
            conditions = [
                DBCondition(
                    namespace_id=namespace.id,
                    name=f"condition_{namespace.app_id:09d}_{namespace.id:09d}_{i:09d}",
                    display_name=f"Condition {namespace.app_id} {namespace.id} {i}",
                    documentation=f"Doc {namespace.app_id} {namespace.id} {i}",
                    parameters="a,b,c",
                    code=b64encode(b"CODE"),
                )
                for i in range(conditions_per_namespace)
                for namespace in namespaces
            ]
            session.add_all(conditions)
        async with session.begin():
            [
                await session.refresh(condition, attribute_names=["namespace"])
                for condition in conditions
            ]
        return conditions

    return _create_conditions
