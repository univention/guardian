# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


import pytest
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.main import app

DEFAULT_TEST_APP = "app"
DEFAULT_TEST_NAMESPACE = "namespace"


@pytest.mark.usefixtures("create_tables")
class TestNamespaceEndpoints:
    @pytest.mark.asyncio
    async def test_post_namespace(self, client, create_app, sqlalchemy_mixin):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
        namespace_name = "new-namespace"
        response = client.post(
            app.url_path_for("create_namespace", app_name=DEFAULT_TEST_APP),
            json={
                "name": namespace_name,
                "display_name": "test",
            },
        )
        assert response.status_code == 200, response.json()
        assert response.json() == {
            "namespace": {
                "app_name": DEFAULT_TEST_APP,
                "name": namespace_name,
                "display_name": "test",
                "resource_url": f"{COMPLETE_URL}/namespaces/{DEFAULT_TEST_APP}/{namespace_name}",
            }
        }

    def test_post_app_non_existing_raises_404(self, client):
        app_name = "non-existing-app"
        response = client.post(
            app.url_path_for("create_namespace", app_name=app_name),
            json={
                "name": "some-namespace",
                "display_name": "test",
            },
        )
        assert response.status_code == 404, response.json()

    @pytest.mark.asyncio
    async def test_post_namespace_exists_raises_409(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_namespace(session)
        response = client.post(
            app.url_path_for("create_namespace", app_name=DEFAULT_TEST_APP),
            json={
                "name": DEFAULT_TEST_NAMESPACE,
            },
        )
        assert response.status_code == 409, response.json()

    @pytest.mark.asyncio
    async def test_get_namespace(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_namespace(session)
        response = client.get(
            app.url_path_for(
                "get_namespace", app_name=DEFAULT_TEST_APP, name=DEFAULT_TEST_NAMESPACE
            ),
        )
        assert response.status_code == 200, response.json()
        assert response.json() == {
            "namespace": {
                "app_name": DEFAULT_TEST_APP,
                "display_name": "Namespace",
                "name": DEFAULT_TEST_NAMESPACE,
                "resource_url": f"http://localhost:8001/guardian/management/namespaces/{DEFAULT_TEST_APP}/{DEFAULT_TEST_NAMESPACE}",
            }
        }

    def test_get_namespace_404_app(self, client):
        app_name = "non-existing-app"
        response = client.get(
            app.url_path_for(
                "get_namespace", app_name=app_name, name=DEFAULT_TEST_NAMESPACE
            ),
        )
        assert response.status_code == 404, response.json()

    @pytest.mark.asyncio
    async def test_get_namespace_non_existing(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)

        namespace_name = "non-existing-namespace"
        response = client.get(
            app.url_path_for(
                "get_namespace", app_name=DEFAULT_TEST_APP, name=namespace_name
            ),
        )
        assert response.status_code == 404, response.json()

    @pytest.mark.asyncio
    async def test_get_all_namespaces(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_namespace(session, name="test-namespace1")
            await create_namespace(session, name="test-namespace2")

        response = client.get(app.url_path_for("get_all_namespaces"))
        assert response.status_code == 200
        assert response.json() == {
            "namespaces": [
                {
                    "app_name": DEFAULT_TEST_APP,
                    "display_name": "Namespace",
                    "name": "test-namespace1",
                    "resource_url": f"http://localhost:8001/guardian/management/namespaces/{DEFAULT_TEST_APP}/test-namespace1",
                },
                {
                    "app_name": DEFAULT_TEST_APP,
                    "display_name": "Namespace",
                    "name": "test-namespace2",
                    "resource_url": f"http://localhost:8001/guardian/management/namespaces/{DEFAULT_TEST_APP}/test-namespace2",
                },
            ],
            "pagination": {"limit": 2, "offset": 0, "total_count": 2},
        }

    @pytest.mark.asyncio
    async def test_get_all_namespaces_for_app(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
    ):
        app_name = "test-app2"

        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_app(session, name=app_name)
            await create_namespace(session, name="test-namespace1")
            await create_namespace(session, name="test-namespace2", app_name=app_name)
        response = client.get(
            app.url_path_for("get_namespaces_by_app", app_name=app_name)
        )
        assert response.status_code == 200
        assert response.json() == {
            "namespaces": [
                {
                    "app_name": app_name,
                    "display_name": "Namespace",
                    "name": "test-namespace2",
                    "resource_url": f"http://localhost:8001/guardian/management/namespaces/{app_name}/test-namespace2",
                },
            ],
            "pagination": {"limit": 1, "offset": 0, "total_count": 1},
        }

    @pytest.mark.asyncio
    async def test_get_all_namespaces_for_app_non_existing_app_no_result(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_namespace(session, name="test-namespace1")
        app_name = "non-existing-app"
        response = client.get(
            app.url_path_for("get_namespaces_by_app", app_name=app_name)
        )
        assert response.status_code == 200, {
            "namespaces": [],
            "pagination": {"limit": 0, "offset": 0, "total_count": 0},
        }

    @pytest.mark.asyncio
    async def test_get_all_namespaces_limit_and_offset(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_namespace(session, name="test-namespace1")
            await create_namespace(session, name="test-namespace2")

        response = client.get(
            app.url_path_for("get_all_namespaces") + "?limit=1&offset=1"
        )
        assert response.status_code == 200
        assert response.json() == {
            "namespaces": [
                {
                    "app_name": DEFAULT_TEST_APP,
                    "display_name": "Namespace",
                    "name": "test-namespace2",
                    "resource_url": f"http://localhost:8001/guardian/management/namespaces/{DEFAULT_TEST_APP}/test-namespace2",
                }
            ],
            "pagination": {"limit": 1, "offset": 1, "total_count": 2},
        }

    @pytest.mark.asyncio
    async def test_patch_namespace(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_namespace(session)

        changed_display_name = "changed_display_name"
        response = client.patch(
            app.url_path_for(
                "edit_namespace", app_name=DEFAULT_TEST_APP, name=DEFAULT_TEST_NAMESPACE
            ),
            json={"display_name": changed_display_name},
        )
        assert response.status_code == 201, response.json()
        assert response.json() == {
            "namespace": {
                "app_name": DEFAULT_TEST_APP,
                "name": DEFAULT_TEST_NAMESPACE,
                "display_name": changed_display_name,
                "resource_url": f"{COMPLETE_URL}/namespaces/{DEFAULT_TEST_APP}/{DEFAULT_TEST_NAMESPACE}",
            }
        }

    def test_patch_namespace_non_existing_app_raises(self, client):
        changed_display_name = "changed_display_name"
        response = client.patch(
            app.url_path_for(
                "edit_namespace",
                app_name="non-existing-app",
                name=DEFAULT_TEST_NAMESPACE,
            ),
            json={"display_name": changed_display_name},
        )
        assert response.status_code == 404, response.json()

    @pytest.mark.asyncio
    async def test_patch_namespace_non_existing_namespace_raises(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
        namespace_name = "non-existing-namespace"
        changed_display_name = "changed_display_name"
        response = client.patch(
            app.url_path_for(
                "edit_namespace", app_name=DEFAULT_TEST_APP, name=namespace_name
            ),
            json={"display_name": changed_display_name},
        )
        assert response.status_code == 404, response.json()
