# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


import pytest
from fastapi.testclient import TestClient
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.main import app


@pytest.mark.e2e
class TestAppEndpoints:
    @pytest.fixture(autouse=True)
    def client(self):
        return TestClient(app)

    @pytest.mark.usefixtures("create_tables")
    def test_post_app_minimal(self, client, register_test_adapters):
        response = client.post(
            app.url_path_for("create_app"), json={"name": "test_app"}
        )
        assert response.status_code == 200
        assert response.json() == {
            "app": {
                "display_name": None,
                "name": "test_app",
                "resource_url": f"{COMPLETE_URL}/apps/test_app",
            }
        }

    @pytest.mark.usefixtures("create_tables")
    def test_post_app_all(self, client, register_test_adapters):
        response = client.post(
            app.url_path_for("create_app"),
            json={"name": "test_app", "display_name": "test_app display_name"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "app": {
                "display_name": "test_app display_name",
                "name": "test_app",
                "resource_url": f"{COMPLETE_URL}/apps/test_app",
            }
        }

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_get_app(
        self, client, register_test_adapters, create_app, sqlalchemy_mixin
    ):
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
    def test_get_app_404(self, client, register_test_adapters):
        name: str = "test_app3"
        response = client.get(app.url_path_for("get_app", name=name))
        assert response.status_code == 404

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_get_all_apps(
        self, client, register_test_adapters, create_apps, sqlalchemy_mixin
    ):
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
        self, client, register_test_adapters, create_apps, sqlalchemy_mixin
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
    async def test_patch_app(
        self, client, register_test_adapters, create_app, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, "test_app2", display_name=None)
        response = client.patch(
            app.url_path_for("edit_app", name="test_app2"),
            json={"name": "test_app2", "display_name": "expected displayname"},
        )
        assert response.status_code == 201
        assert response.json() == {
            "app": {
                "display_name": "expected displayname",
                "name": "test_app2",
                "resource_url": f"{COMPLETE_URL}/apps/test_app2",
            }
        }

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_patch_non_existing_app_fails(self, client, register_test_adapters):
        response = client.patch(
            app.url_path_for("edit_app", name="non-existing"),
            json={"name": "non-existing", "display_name": "displayname"},
        )
        assert response.status_code == 404
