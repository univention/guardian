# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import asyncio
import os
import subprocess
from base64 import b64encode
from pathlib import Path
from typing import Optional, Tuple
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from guardian_lib.adapter_registry import ADAPTER_REGISTRY
from guardian_lib.adapters.authentication import FastAPIAlwaysAuthorizedAdapter
from guardian_lib.adapters.settings import EnvSettingsAdapter
from guardian_lib.ports import AuthenticationPort, SettingsPort
from guardian_management_api.adapters.app import (
    FastAPIAppAPIAdapter,
    SQLAppPersistenceAdapter,
)
from guardian_management_api.adapters.authz import (
    AlwaysAuthorizedAdapter,
    GuardianAuthorizationAdapter,
)
from guardian_management_api.adapters.bundle_server import BundleServerAdapter
from guardian_management_api.adapters.capability import (
    FastAPICapabilityAPIAdapter,
    SQLCapabilityPersistenceAdapter,
)
from guardian_management_api.adapters.condition import (
    FastAPIConditionAPIAdapter,
    SQLConditionPersistenceAdapter,
)
from guardian_management_api.adapters.context import (
    FastAPIContextAPIAdapter,
    SQLContextPersistenceAdapter,
)
from guardian_management_api.adapters.namespace import (
    FastAPINamespaceAPIAdapter,
    SQLNamespacePersistenceAdapter,
)
from guardian_management_api.adapters.permission import (
    FastAPIPermissionAPIAdapter,
    SQLPermissionPersistenceAdapter,
)
from guardian_management_api.adapters.role import (
    FastAPIRoleAPIAdapter,
    SQLRolePersistenceAdapter,
)
from guardian_management_api.adapters.sql_persistence import SQLAlchemyMixin
from guardian_management_api.main import app
from guardian_management_api.models.capability import CapabilityConditionRelation
from guardian_management_api.models.condition import ConditionParameterType
from guardian_management_api.models.sql_persistence import (
    Base,
    DBApp,
    DBCapability,
    DBCapabilityCondition,
    DBCondition,
    DBConditionParameter,
    DBContext,
    DBNamespace,
    DBPermission,
    DBRole,
)
from guardian_management_api.ports.app import (
    AppAPIPort,
    AppPersistencePort,
)
from guardian_management_api.ports.authz import ResourceAuthorizationPort
from guardian_management_api.ports.bundle_server import BundleServerPort
from guardian_management_api.ports.capability import (
    CapabilityAPIPort,
    CapabilityPersistencePort,
)
from guardian_management_api.ports.condition import (
    ConditionAPIPort,
    ConditionPersistencePort,
)
from guardian_management_api.ports.context import ContextAPIPort, ContextPersistencePort
from guardian_management_api.ports.namespace import (
    NamespaceAPIPort,
    NamespacePersistencePort,
)
from guardian_management_api.ports.permission import (
    PermissionAPIPort,
    PermissionPersistencePort,
)
from guardian_management_api.ports.role import (
    RoleAPIPort,
    RolePersistencePort,
)
from port_loader import AsyncAdapterRegistry, AsyncAdapterSettingsProvider
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from starlette.testclient import TestClient


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


def pytest_addoption(parser):
    parser.addoption(
        "--real_db",
        action="store_true",
        default=False,
        help="Use the database set by the environment variables "
        "instead of the db provided by fixture 'sqlite_db_name'. "
        "If a database other then sqlite is used, all SQL_PERSISTENCE_* "
        "environment variables have to be set in the environment. "
        "Never run this against a production database! Tables will be dropped.",
    )


@pytest.fixture(scope="session")
def patch_env(sqlite_db_name, bundle_server_base_dir, pytestconfig):
    _environ = os.environ.copy()
    os.environ["GUARDIAN__MANAGEMENT__BUNDLE_SERVER__DISABLED"] = "1"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__APP_PERSISTENCE_PORT"] = "sql"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__CONDITION_PERSISTENCE_PORT"] = "sql"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__CONTEXT_PERSISTENCE_PORT"] = "sql"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__NAMESPACE_PERSISTENCE_PORT"] = "sql"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__PERMISSION_PERSISTENCE_PORT"] = "sql"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__ROLE_PERSISTENCE_PORT"] = "sql"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__CAPABILITY_PERSISTENCE_PORT"] = "sql"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__SETTINGS_PORT"] = "env"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__APP_API_PORT"] = "APP_API_PORT"
    if pytestconfig.getoption("real_db"):
        os.environ["SQL_PERSISTENCE_ADAPTER__DIALECT"] = os.environ.get(
            "SQL_PERSISTENCE_ADAPTER__DIALECT", "sqlite"
        )
        os.environ["SQL_PERSISTENCE_ADAPTER__DB_NAME"] = os.environ.get(
            "SQL_PERSISTENCE_ADAPTER__DB_NAME", sqlite_db_name
        )
    else:
        os.environ["SQL_PERSISTENCE_ADAPTER__DIALECT"] = "sqlite"
        os.environ["SQL_PERSISTENCE_ADAPTER__DB_NAME"] = sqlite_db_name
    os.environ["BUNDLE_SERVER_ADAPTER__BASE_DIR"] = bundle_server_base_dir
    os.environ["BUNDLE_SERVER_ADAPTER__POLICY_BUNDLE_TEMPLATE_SRC"] = str(
        Path(__file__).parents[1] / "rego_policy_bundle_template"
    )
    os.environ[
        "GUARDIAN__MANAGEMENT__ADAPTER__AUTHENTICATION_PORT"
    ] = "fast_api_always_authorized"
    os.environ["GUARDIAN__MANAGEMENT__ADAPTER__RESOURCE_AUTHORIZATION_PORT"] = "always"
    if "OAUTH_ADAPTER__WELL_KNOWN_URL" not in os.environ:
        os.environ["OAUTH_ADAPTER__WELL_KNOWN_URL"] = "/dev/zero"
    yield
    os.environ.clear()
    os.environ.update(_environ)


@pytest_asyncio.fixture(scope="session")
async def client(patch_env):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def registry_test_adapters(patch_env):
    """Fixture that returns a registers with test adapters."""

    registry = AsyncAdapterRegistry()
    for port, adapter in [
        (SettingsPort, EnvSettingsAdapter),
        (AppPersistencePort, SQLAppPersistenceAdapter),
        (ConditionPersistencePort, SQLConditionPersistenceAdapter),
        (ContextPersistencePort, SQLContextPersistenceAdapter),
        (NamespacePersistencePort, SQLNamespacePersistenceAdapter),
        (PermissionPersistencePort, SQLPermissionPersistenceAdapter),
        (CapabilityPersistencePort, SQLCapabilityPersistenceAdapter),
        (RolePersistencePort, SQLRolePersistenceAdapter),
        (AppAPIPort, FastAPIAppAPIAdapter),
        (NamespaceAPIPort, FastAPINamespaceAPIAdapter),
        (ConditionAPIPort, FastAPIConditionAPIAdapter),
        (BundleServerPort, BundleServerAdapter),
        (PermissionAPIPort, FastAPIPermissionAPIAdapter),
        (CapabilityAPIPort, FastAPICapabilityAPIAdapter),
        (RoleAPIPort, FastAPIRoleAPIAdapter),
        (ContextAPIPort, FastAPIContextAPIAdapter),
        (AuthenticationPort, FastAPIAlwaysAuthorizedAdapter),
        (ResourceAuthorizationPort, AlwaysAuthorizedAdapter),
    ]:
        registry.register_port(port)
        registry.register_adapter(port, adapter_cls=adapter)
        registry.set_adapter(port, adapter)
    registry.register_adapter(
        AsyncAdapterSettingsProvider, adapter_cls=EnvSettingsAdapter
    )
    registry.set_adapter(AsyncAdapterSettingsProvider, EnvSettingsAdapter)

    return registry


@pytest.fixture(scope="session")
def sqlite_db_name(tmpdir_factory):
    sqlite_db_name = tmpdir_factory.mktemp("db").join("management.db")
    return str(sqlite_db_name)


@pytest.fixture(scope="session")
def bundle_server_base_dir(tmpdir_factory):
    bundle_dir = tmpdir_factory.mktemp("bundle_server")
    return str(bundle_dir)


@pytest.fixture
def sqlite_url(sqlite_db_name):
    return f"///{sqlite_db_name}"


def db_url():
    db_name = os.environ["SQL_PERSISTENCE_ADAPTER__DB_NAME"]
    host = os.environ["SQL_PERSISTENCE_ADAPTER__HOST"]
    port = os.environ["SQL_PERSISTENCE_ADAPTER__PORT"]
    username = os.environ["SQL_PERSISTENCE_ADAPTER__USERNAME"]
    password = os.environ["SQL_PERSISTENCE_ADAPTER__PASSWORD"]
    return f"{username}:{password}@{host}:{port}/{db_name}"


@pytest_asyncio.fixture(scope="function")
async def create_tables(sqlite_url, patch_env, sqlite_db_name, pytestconfig):
    dialect = os.environ.get("SQL_PERSISTENCE_ADAPTER__DIALECT")
    if dialect in [None, "sqlite"]:
        if pytestconfig.getoption("real_db"):
            url = f"sqlite+aiosqlite://{db_url()}"
        else:
            url = f"sqlite+aiosqlite://{sqlite_url}"
    elif dialect == "postgresql":
        url = f"postgresql+asyncpg://{db_url()}"
    else:
        raise Exception(f"Unknown dialect: '{dialect}'")

    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    if dialect not in [None, "sqlite"] or pytestconfig.getoption("real_db"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    else:
        os.remove(sqlite_db_name)


@pytest.fixture
def run_alembic_migrations(patch_env, sqlite_db_name):
    try:
        subprocess.check_call(
            ["python3", "-m", "alembic", "downgrade", "base"],
            cwd=Path(__file__).parents[1],
        )
    except subprocess.CalledProcessError:
        pass  # we do not care if everything after works.
    subprocess.check_call(
        ["python3", "-m", "alembic", "upgrade", "head"], cwd=Path(__file__).parents[1]
    )
    yield
    subprocess.check_call(
        ["python3", "-m", "alembic", "downgrade", "base"], cwd=Path(__file__).parents[1]
    )
    try:
        os.remove(sqlite_db_name)
    except FileNotFoundError:
        pass


@pytest.fixture
def sqlalchemy_mixin(sqlite_url, pytestconfig):
    dialect = os.environ.get("SQL_PERSISTENCE_ADAPTER__DIALECT")
    mixin = SQLAlchemyMixin()
    if dialect in [None, "sqlite"]:
        if pytestconfig.getoption("real_db"):
            db_name = os.environ.get("SQL_PERSISTENCE_ADAPTER__DB_NAME")
            mixin._db_string = SQLAlchemyMixin.create_db_string(
                "sqlite", "", "", db_name, "", ""
            )
        else:
            mixin._db_string = SQLAlchemyMixin.create_db_string(
                "sqlite", "", "", sqlite_url, "", ""
            )
    elif dialect == "postgresql":
        mixin._db_string = SQLAlchemyMixin.create_db_string(
            "postgresql",
            os.environ.get("SQL_PERSISTENCE_ADAPTER__HOST"),
            os.environ.get("SQL_PERSISTENCE_ADAPTER__PORT"),
            os.environ.get("SQL_PERSISTENCE_ADAPTER__DB_NAME"),
            os.environ.get("SQL_PERSISTENCE_ADAPTER__USERNAME"),
            os.environ.get("SQL_PERSISTENCE_ADAPTER__PASSWORD"),
        )
    else:
        raise Exception(f"Unknown dialect: '{dialect}'")
    return mixin


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
        parameters: Optional[list[Tuple[str, ConditionParameterType]]] = None,
        code: Optional[bytes] = None,
    ):
        if parameters is None:
            parameters = [
                ("a", ConditionParameterType.ANY),
                ("b", ConditionParameterType.ANY),
            ]
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
                parameters=[
                    DBConditionParameter(
                        name=cond_param[0], value_type=cond_param[1], position=idx
                    )
                    for idx, cond_param in enumerate(parameters)
                ],
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
                    parameters=[
                        DBConditionParameter(
                            name=cond_param[0], value_type=cond_param[1], position=idx
                        )
                        for idx, cond_param in enumerate(
                            [
                                ("a", ConditionParameterType.ANY),
                                ("b", ConditionParameterType.ANY),
                                ("c", ConditionParameterType.ANY),
                            ]
                        )
                    ],
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


@pytest.fixture
def create_capabilities(
    create_role, create_permission, create_condition, create_namespaces
):
    async def _create_capabilities(
        session: AsyncSession,
        capabilities_per_role: int,
        num_roles: int = 1,
    ) -> list[DBCapability]:
        db_namespace = (await create_namespaces(session, 1))[0]
        db_app = db_namespace.app
        db_roles = [
            await create_role(session, db_app.name, db_namespace.name, f"role_{i:09d}")
            for i in range(num_roles)
        ]
        caps = []
        for db_role in db_roles:
            db_permission = await create_permission(
                session,
                db_app.name,
                db_namespace.name,
                f"cap_permission_{db_role.name}",
            )
            db_condition = await create_condition(
                session,
                app_name=db_app.name,
                namespace_name=db_namespace.name,
                name=f"cap_condition_{db_role.name}",
            )
            caps.extend(
                [
                    DBCapability(
                        namespace_id=db_namespace.id,
                        role_id=db_role.id,
                        name=f"capability_{i:09d}_{db_role.name}",
                        relation=CapabilityConditionRelation.AND,
                        permissions={db_permission},
                        conditions={
                            DBCapabilityCondition(
                                condition_id=db_condition.id,
                                kwargs=[
                                    {"name": "a", "value": True},
                                    {"name": "b", "value": 1},
                                ],
                            )
                        },
                    )
                    for i in range(capabilities_per_role)
                ]
            )
        async with session.begin():
            [session.add(cap) for cap in caps]
        [await session.refresh(cap) for cap in caps]
        return caps

    return _create_capabilities


@pytest.fixture
def create_capability(
    create_app, create_namespace, create_condition, create_permission, create_role
):
    async def _create_capability(
        session: AsyncSession,
        name: str = "capability",
        display_name: str = "Capability",
        app_name: str = "app",
        namespace_name: str = "namespace",
    ) -> DBCapability:
        await create_app(session=session, name=app_name)
        namespace = await create_namespace(
            session=session, app_name=app_name, name=namespace_name
        )
        condition = await create_condition(
            session=session, app_name=app_name, namespace_name=namespace_name
        )
        permission = await create_permission(
            session=session, app_name=app_name, namespace_name=namespace_name
        )
        role = await create_role(
            session=session, app_name=app_name, namespace_name=namespace_name
        )
        async with session.begin():
            capability = DBCapability(
                namespace_id=namespace.id,
                role_id=role.id,
                name=name,
                display_name=display_name,
                relation=CapabilityConditionRelation.AND,
                permissions={permission},
                conditions={
                    DBCapabilityCondition(
                        condition_id=condition.id,
                        kwargs=[
                            {"name": "a", "value": True},
                            {"name": "b", "value": 1},
                        ],
                    )
                },
            )
            session.add(capability)
        async with session.begin():
            await session.refresh(capability, attribute_names=["namespace"])
        return capability

    return _create_capability


@pytest_asyncio.fixture(scope="function")
async def set_up_auth():
    _original_resource_authorization_adapter = AlwaysAuthorizedAdapter
    ADAPTER_REGISTRY.set_adapter(
        ResourceAuthorizationPort, GuardianAuthorizationAdapter
    )
    adapter = await ADAPTER_REGISTRY.request_adapter(
        AuthenticationPort, FastAPIAlwaysAuthorizedAdapter
    )
    _original_get_actor_identifier = adapter.get_actor_identifier
    adapter.get_actor_identifier = AsyncMock(
        return_value="uid=guardian,cn=users,dc=school,dc=test"
    )
    yield
    ADAPTER_REGISTRY.set_adapter(
        ResourceAuthorizationPort, _original_resource_authorization_adapter
    )
    adapter.get_actor_identifier = _original_get_actor_identifier


@pytest.fixture
def base_url() -> str:
    return os.getenv("GUARDIAN__MANAGEMENT__BASE_URL", "http://localhost:8001")
