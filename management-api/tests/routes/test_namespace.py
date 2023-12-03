# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


import os

import pytest
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.main import app
from guardian_management_api.models.sql_persistence import (
    DBNamespace,
)
from sqlalchemy import select

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
        assert response.status_code == 201, response.json()
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
        assert response.status_code == 400, response.json()
        assert response.json() == {
            "detail": {
                "message": "An object with the given identifiers already exists."
            }
        }

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


@pytest.mark.e2e
@pytest.mark.skipif(
    "UCS_HOST_IP" not in os.environ,
    reason="UCS_HOST_IP env var not set",
)
class TestNamespaceEndpointsAuthorization:
    @pytest.mark.asyncio
    async def test_get_guardian_namespace_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(
                session=session,
                name="guardian",
            )
            await create_namespace(
                session=session,
                display_name=None,
                app_name="guardian",
                name="namespace",
            )
        response = client.get(
            app.url_path_for(
                "get_namespace",
                name="namespace",
                app_name="guardian",
            ),
        )
        assert response.status_code == 200
        assert response.json()["namespace"]["name"] == "namespace"

    @pytest.mark.asyncio
    async def test_get_other_namespace_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(
                session=session,
                name="other",
            )
            await create_namespace(
                session=session,
                display_name=None,
                app_name="other",
                name="namespace",
            )
        response = client.get(
            app.url_path_for(
                "get_namespace",
                name="namespace",
                app_name="other",
            ),
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_all_namespaces(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(
                session=session,
                name="guardian",
            )
            await create_namespace(
                session=session,
                display_name=None,
                app_name="guardian",
                name="namespace",
            )
        async with sqlalchemy_mixin.session() as session:
            await create_app(
                session=session,
                name="other",
            )
            await create_namespace(
                session=session,
                display_name=None,
                app_name="other",
                name="namespace",
            )
        response = client.get(
            app.url_path_for("get_all_namespaces"),
        )
        assert response.status_code == 200
        assert any(
            namespace["name"] == "namespace"
            for namespace in response.json()["namespaces"]
        )
        assert not any(
            namespace["name"] == "other" for namespace in response.json()["namespaces"]
        )

    @pytest.mark.asyncio
    async def test_patch_guardian_namespace_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(
                session=session,
                name="guardian",
            )
            await create_namespace(
                session=session,
                display_name=None,
                app_name="guardian",
                name="namespace",
            )
        response = client.patch(
            app.url_path_for(
                "edit_namespace",
                name="namespace",
                app_name="guardian",
            ),
            json={
                "display_name": "expected displayname",
                "permissions": [],
                "conditions": [],
                "relation": "AND",
                "role": {
                    "app_name": "guardian",
                    "namespace_name": "namespace",
                    "name": "role",
                },
            },
        )
        assert response.status_code == 201
        assert response.json()["namespace"]["name"] == "namespace"
        assert response.json()["namespace"]["display_name"] == "expected displayname"

    @pytest.mark.asyncio
    async def test_patch_other_namespace_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(
                session=session,
                name="other",
            )
            await create_namespace(
                session=session,
                display_name=None,
                app_name="other",
                name="namespace",
            )
        response = client.patch(
            app.url_path_for(
                "edit_namespace",
                name="namespace",
                app_name="other",
            ),
            json={
                "display_name": "expected displayname",
                "permissions": [],
                "relation": "AND",
                "role": {
                    "app_name": "other",
                    "namespace_name": "namespace",
                    "name": "role",
                },
            },
        )
        assert response.status_code == 403

        # check that the namespace was not updated in the database
        async with sqlalchemy_mixin.session() as session:
            db_cap = (
                (await session.execute(select(DBNamespace).filter_by(name="namespace")))
                .unique()
                .scalar_one_or_none()
            )
            assert db_cap.display_name is None

    @pytest.mark.asyncio
    async def test_create_namespace_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(
                session=session,
                name="other",
            )
            # easiest way to setup app, namespace, roles...
            await create_namespace(
                session=session,
                name="test2",
                display_name=None,
                app_name="other",
            )
        response = client.post(
            app.url_path_for("create_namespace", app_name="other"),
            json={
                "name": "test3",
                "display_name": "expected displayname",
                "permissions": [],
                "conditions": [],
                "relation": "AND",
                "role": {
                    "app_name": "other",
                    "namespace_name": "namespace",
                    "name": "role",
                },
            },
        )
        assert response.status_code == 403

        # check that the namespace was not created in the database
        async with sqlalchemy_mixin.session() as session:
            db_cap = (
                (await session.execute(select(DBNamespace).filter_by(name="test3")))
                .unique()
                .scalar_one_or_none()
            )
            assert db_cap is None

    @pytest.mark.asyncio
    async def test_get_namespaces_by_app(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(
                session=session,
                name="guardian",
            )
            await create_namespace(
                session=session,
                name="test",
                display_name=None,
                app_name="guardian",
            )
        response = client.get(
            app.url_path_for(
                "get_namespaces_by_app",
                app_name="guardian",
            ),
        )
        assert response.status_code == 200
        assert any(
            namespace["name"] == "test" for namespace in response.json()["namespaces"]
        )
        assert not any(
            namespace["name"] == "other" for namespace in response.json()["namespaces"]
        )

    @pytest.mark.asyncio
    async def test_get_namespaces_by_app_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(
                session=session,
                name="other",
            )
            await create_namespace(
                session=session,
                name="test",
                display_name=None,
                app_name="other",
            )

        response = client.get(
            app.url_path_for(
                "get_namespaces_by_app",
                app_name="other",
            ),
        )

        assert response.status_code == 200
        assert not any(
            namespace["name"] == "test" for namespace in response.json()["namespaces"]
        )
