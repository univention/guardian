# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


import os
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from guardian_lib.adapter_registry import ADAPTER_REGISTRY
from guardian_lib.adapters.authentication import FastAPIAlwaysAuthorizedAdapter
from guardian_lib.ports import AuthenticationPort
from guardian_management_api.adapters.authz import GuardianAuthorizationAdapter
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.main import app
from guardian_management_api.models.capability import CapabilityConditionRelation
from guardian_management_api.models.routers.app import App as ResponseApp
from guardian_management_api.models.routers.app import (
    AppAdmin,
    AppDefaultNamespace,
    AppRegisterResponse,
)
from guardian_management_api.models.routers.base import ManagementObjectName
from guardian_management_api.models.sql_persistence import (
    DBCapability,
)
from guardian_management_api.ports.authz import ResourceAuthorizationPort
from sqlalchemy import select


@pytest.mark.e2e
class TestAppEndpoints:
    @pytest.mark.usefixtures("create_tables")
    def test_post_app_minimal(self, client):
        response = client.post(
            app.url_path_for("create_app"), json={"name": "test_app"}
        )
        assert response.status_code == 201
        assert response.json() == {
            "app": {
                "display_name": None,
                "name": "test_app",
                "resource_url": f"{COMPLETE_URL}/apps/test_app",
            }
        }

    @pytest.mark.usefixtures("create_tables")
    def test_post_app_validation_error(self, client):
        response = client.post(
            app.url_path_for("create_app"), json={"name": "invalid app #name"}
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "name"],
                    "msg": 'string does not match regex "^[a-z][a-z0-9\\-_]*$"',
                    "type": "value_error.str.regex",
                    "ctx": {"pattern": "^[a-z][a-z0-9\\-_]*$"},
                }
            ]
        }

    @pytest.mark.usefixtures("create_tables")
    def test_post_app_all(self, client):
        response = client.post(
            app.url_path_for("create_app"),
            json={"name": "test_app", "display_name": "test_app display_name"},
        )
        assert response.status_code == 201
        assert response.json() == {
            "app": {
                "display_name": "test_app display_name",
                "name": "test_app",
                "resource_url": f"{COMPLETE_URL}/apps/test_app",
            }
        }

    @pytest.mark.usefixtures("run_alembic_migrations")
    @pytest.mark.asyncio
    async def test_register_app(self, client, sqlalchemy_mixin):
        response = client.post(
            client.app.url_path_for("register_app"),
            json={"name": "app1", "display_name": "App 1"},
        )
        assert response.status_code == 201
        assert (
            response.json()
            == AppRegisterResponse(
                app=ResponseApp(
                    name=ManagementObjectName("app1"),
                    display_name="App 1",
                    resource_url=f"{COMPLETE_URL}/guardian/management/apps/app1",
                ),
                admin_role=AppAdmin(
                    app_name=ManagementObjectName("app1"),
                    namespace_name=ManagementObjectName("default"),
                    name=ManagementObjectName("app-admin"),
                    display_name="App Administrator for App 1",
                    resource_url=f"{COMPLETE_URL}/roles/app1/default/app-admin",
                ),
                default_namespace=AppDefaultNamespace(
                    app_name=ManagementObjectName("app1"),
                    name=ManagementObjectName("default"),
                    display_name="Default Namespace for App 1",
                    resource_url=f"{COMPLETE_URL}/namespaces/app1/default",
                ),
            ).dict()
        )
        async with sqlalchemy_mixin.session() as session:
            result = list(
                (await session.execute(select(DBCapability))).unique().scalars()
            )
            assert len(result) == 6, [
                o.name for o in result
            ]  # The four builtin plus 2 new
            admin_cap = await session.scalar(
                select(DBCapability).where(DBCapability.name == "app1-admin-cap")
            )
            admin_cap_readonly = await session.scalar(
                select(DBCapability).where(
                    DBCapability.name == "app1-admin-cap-read-role-cond"
                )
            )
            assert {
                f"{perm.namespace.app.name}:{perm.namespace.name}:{perm.name}"
                for perm in admin_cap.permissions
            } == {
                f"guardian:management-api:{name}"
                for name in (
                    "create_resource",
                    "update_resource",
                    "read_resource",
                    "delete_resource",
                )
            }
            assert len(admin_cap.conditions) == 1
            cond = set(admin_cap.conditions).pop()
            assert (
                f"{cond.condition.namespace.app.name}:{cond.condition.namespace.name}:{cond.condition.name}"
                == "guardian:builtin:target_field_equals_value"
            )
            assert cond.kwargs == [
                {"name": "field", "value": "app_name", "value_type": "STRING"},
                {"name": "value", "value": "app1", "value_type": "ANY"},
            ]
            assert (
                f"{admin_cap.role.namespace.app.name}:{admin_cap.role.namespace.name}:{admin_cap.role.name}"
                == "app1:default:app-admin"
            )
            assert {
                f"{perm.namespace.app.name}:{perm.namespace.name}:{perm.name}"
                for perm in admin_cap_readonly.permissions
            } == {"guardian:management-api:read_resource"}
            assert admin_cap_readonly.relation == CapabilityConditionRelation.OR
            assert len(admin_cap_readonly.conditions) == 2

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_register_app_exists_error(
        self, client, sqlalchemy_mixin, create_app
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, name="app1")
        response = client.post(
            client.app.url_path_for("register_app"),
            json={"name": "app1", "display_name": "App 1"},
        )
        assert response.status_code == 400

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_create_app_validation_error(
        self, client, sqlalchemy_mixin, create_app
    ):
        response = client.post(
            client.app.url_path_for("register_app"),
            json={"not_name": "app1"},
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "name"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        }

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_get_app(self, client, create_app, sqlalchemy_mixin):
        name: str = "test_app2"
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, name=name, display_name=None)
        response = client.get(app.url_path_for("get_app", name=name))
        assert response.status_code == 200
        assert response.json() == {
            "app": {
                "display_name": None,
                "name": "test_app2",
                "resource_url": f"{COMPLETE_URL}/apps/test_app2",
            }
        }

    @pytest.mark.usefixtures("create_tables")
    def test_get_app_404(self, client):
        name: str = "test_app3"
        response = client.get(app.url_path_for("get_app", name=name))
        assert response.status_code == 404

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_get_all_apps(self, client, create_apps, sqlalchemy_mixin):
        async with sqlalchemy_mixin.session() as session:
            apps = await create_apps(session, 2)
        response = client.get(app.url_path_for("get_all_apps"))
        assert response.status_code == 200
        assert response.json() == {
            "apps": [
                {
                    "display_name": apps[0].display_name,
                    "name": apps[0].name,
                    "resource_url": f"{COMPLETE_URL}/apps/{apps[0].name}",
                },
                {
                    "display_name": apps[1].display_name,
                    "name": apps[1].name,
                    "resource_url": f"{COMPLETE_URL}/apps/{apps[1].name}",
                },
            ],
            "pagination": {"limit": 2, "offset": 0, "total_count": 2},
        }

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_get_all_apps_limit_and_offset(
        self, client, create_apps, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            apps = await create_apps(session, 2)
        response = client.get(app.url_path_for("get_all_apps") + "?limit=1&offset=1")
        assert response.status_code == 200
        assert response.json() == {
            "apps": [
                {
                    "display_name": apps[1].display_name,
                    "name": apps[1].name,
                    "resource_url": f"{COMPLETE_URL}/apps/{apps[1].name}",
                },
            ],
            "pagination": {"limit": 1, "offset": 1, "total_count": 2},
        }

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_patch_app(self, client, create_app, sqlalchemy_mixin):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, "test_app2", display_name=None)
        response = client.patch(
            app.url_path_for("edit_app", name="test_app2"),
            json={"name": "test_app2", "display_name": "expected displayname"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "app": {
                "display_name": "expected displayname",
                "name": "test_app2",
                "resource_url": f"{COMPLETE_URL}/apps/test_app2",
            }
        }

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_patch_non_existing_app_fails(self, client):
        response = client.patch(
            app.url_path_for("edit_app", name="non-existing"),
            json={"name": "non-existing", "display_name": "displayname"},
        )
        assert response.status_code == 404


@pytest.mark.e2e
@pytest.mark.skipif(
    "UCS_HOST_IP" not in os.environ,
    reason="UCS_HOST_IP env var not set",
)
class TestAppEndpointsAuthorization:
    @staticmethod
    @pytest_asyncio.fixture(scope="function", autouse=True)
    async def set_up_auth():
        ADAPTER_REGISTRY.set_adapter(
            ResourceAuthorizationPort, GuardianAuthorizationAdapter
        )
        adapter = await ADAPTER_REGISTRY.request_adapter(
            AuthenticationPort, FastAPIAlwaysAuthorizedAdapter
        )
        adapter.get_actor_identifier = AsyncMock(
            return_value="uid=guardian,cn=users,dc=school,dc=test"
        )

    @pytest.mark.asyncio
    async def test_get_guardian_app_allowed(
        self, client, create_tables, create_app, sqlalchemy_mixin, set_up_auth
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, "guardian", display_name=None)
        response = client.get(
            app.url_path_for("get_app", name="guardian"),
        )
        assert response.status_code == 200
        assert response.json()["app"]["name"] == "guardian"

    @pytest.mark.asyncio
    async def test_get_other_app_not_allowed(
        self, client, create_tables, create_app, sqlalchemy_mixin, set_up_auth
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, "other", display_name=None)
        response = client.get(
            app.url_path_for("get_app", name="other"),
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_all_apps(
        self, client, create_tables, create_app, sqlalchemy_mixin, set_up_auth
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, "guardian", display_name=None)
            await create_app(session, "other", display_name=None)
        response = client.get(
            app.url_path_for("get_all_apps"),
        )
        assert response.status_code == 200
        assert any(app["name"] == "guardian" for app in response.json()["apps"])
        assert not any(app["name"] == "other" for app in response.json()["apps"])

    @pytest.mark.asyncio
    async def test_patch_guardian_app_allowed(
        self, client, create_tables, create_app, sqlalchemy_mixin, set_up_auth
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, "guardian", display_name=None)
        response = client.patch(
            app.url_path_for("edit_app", name="guardian"),
            json={"display_name": "expected displayname"},
        )
        assert response.status_code == 200
        assert response.json()["app"]["name"] == "guardian"
        assert response.json()["app"]["display_name"] == "expected displayname"

    @pytest.mark.asyncio
    async def test_patch_other_app_not_allowed(
        self, client, create_tables, create_app, sqlalchemy_mixin, set_up_auth
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, "other", display_name=None)
        response = client.patch(
            app.url_path_for("edit_app", name="other"),
            json={"display_name": "expected displayname"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_app_not_allowed(
        self, client, create_tables, create_app, sqlalchemy_mixin, set_up_auth
    ):
        response = client.post(
            app.url_path_for("create_app"),
            json={"name": "other", "display_name": "expected displayname"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_register_app_not_allowed(
        self, client, create_tables, create_app, sqlalchemy_mixin, set_up_auth
    ):
        response = client.post(
            client.app.url_path_for("register_app"),
            json={"name": "other", "display_name": "expected displayname"},
        )
        assert response.status_code == 403
