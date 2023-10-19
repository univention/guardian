# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


import pytest
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.main import app

DEFAULT_TEST_APP = "app"
DEFAULT_TEST_NAMESPACE = "namespace"
DEFAULT_TEST_CONTEXT = "context"


@pytest.mark.usefixtures("create_tables")
class TestContextEndpoints:
    @pytest.mark.asyncio
    async def test_post(
        self,
        client,
        create_app,
        create_namespace,
        sqlalchemy_mixin,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_namespace(session)
        context_name = "new-context"
        response = client.post(
            app.url_path_for(
                "create_context",
                app_name=DEFAULT_TEST_APP,
                namespace_name=DEFAULT_TEST_NAMESPACE,
            ),
            json={
                "name": context_name,
                "display_name": "test",
            },
        )
        assert response.status_code == 200, response.json()
        assert response.json() == {
            "context": {
                "app_name": DEFAULT_TEST_APP,
                "namespace_name": DEFAULT_TEST_NAMESPACE,
                "name": context_name,
                "display_name": "test",
                "resource_url": f"{COMPLETE_URL}/contexts/{DEFAULT_TEST_APP}"
                f"/{DEFAULT_TEST_NAMESPACE}/{context_name}",
            }
        }

    @pytest.mark.asyncio
    async def test_post_409_exists(
        self,
        client,
        create_app,
        create_namespace,
        create_context,
        sqlalchemy_mixin,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_namespace(session)
            await create_context(session)
        response = client.post(
            app.url_path_for(
                "create_context",
                app_name=DEFAULT_TEST_APP,
                namespace_name=DEFAULT_TEST_NAMESPACE,
            ),
            json={
                "name": DEFAULT_TEST_CONTEXT,
                "display_name": "test",
            },
        )
        assert response.status_code == 400
        assert response.json() == {
            "detail": {
                "message": "An object with the given identifiers already exists."
            }
        }

    @pytest.mark.asyncio
    async def test_post_non_existing_app(self, client):
        context_name = "new-context"
        response = client.post(
            app.url_path_for(
                "create_context",
                app_name=DEFAULT_TEST_APP,
                namespace_name=DEFAULT_TEST_NAMESPACE,
            ),
            json={
                "name": context_name,
                "display_name": "test",
            },
        )
        assert response.status_code == 404, response.json()

    @pytest.mark.asyncio
    async def test_post_non_existing_namespace(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)

        context_name = "new-context"
        response = client.post(
            app.url_path_for(
                "create_context",
                app_name=DEFAULT_TEST_APP,
                namespace_name=DEFAULT_TEST_NAMESPACE,
            ),
            json={
                "name": context_name,
                "display_name": "test",
            },
        )
        assert response.status_code == 404, response.json()

    @pytest.mark.asyncio
    async def test_get_context(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
        create_context,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_namespace(session)
            await create_context(session)
        response = client.get(
            app.url_path_for(
                "get_context",
                app_name=DEFAULT_TEST_APP,
                namespace_name=DEFAULT_TEST_NAMESPACE,
                name=DEFAULT_TEST_CONTEXT,
            ),
        )
        assert response.status_code == 200, response.json()
        assert response.json() == {
            "context": {
                "app_name": DEFAULT_TEST_APP,
                "namespace_name": DEFAULT_TEST_NAMESPACE,
                "display_name": "Context",
                "name": DEFAULT_TEST_CONTEXT,
                "resource_url": f"http://localhost:8001/guardian/management/contexts/{DEFAULT_TEST_APP}/{DEFAULT_TEST_NAMESPACE}/{DEFAULT_TEST_CONTEXT}",
            }
        }

    @pytest.mark.asyncio
    async def test_get_context_non_existing_raises_404(
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
                "get_context",
                app_name=DEFAULT_TEST_APP,
                namespace_name=DEFAULT_TEST_NAMESPACE,
                name=DEFAULT_TEST_CONTEXT,
            ),
        )
        assert response.status_code == 404, response.json()

    @pytest.mark.asyncio
    async def test_get_all_contexts(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
        create_context,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_namespace(session)
            await create_context(session, name="context1")
            await create_context(session, name="context2")

        response = client.get(app.url_path_for("get_all_contexts"))
        assert response.status_code == 200
        assert response.json() == {
            "pagination": {"offset": 0, "limit": 2, "total_count": 2},
            "contexts": [
                {
                    "app_name": "app",
                    "namespace_name": "namespace",
                    "name": "context1",
                    "display_name": "Context",
                    "resource_url": "http://localhost:8001/guardian/management/contexts/app/namespace/context1",
                },
                {
                    "app_name": "app",
                    "namespace_name": "namespace",
                    "name": "context2",
                    "display_name": "Context",
                    "resource_url": "http://localhost:8001/guardian/management/contexts/app/namespace/context2",
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_get_contexts_for_app_name(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
        create_context,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_app(session, name="app2")
            await create_namespace(session)
            await create_namespace(session, app_name="app2")
            await create_context(session, name="context1")
            await create_context(session, name="context2", app_name="app2")

        response = client.get(app.url_path_for("get_contexts_by_app", app_name="app2"))
        assert response.status_code == 200
        assert response.json() == {
            "pagination": {"offset": 0, "limit": 1, "total_count": 1},
            "contexts": [
                {
                    "app_name": "app2",
                    "namespace_name": "namespace",
                    "name": "context2",
                    "display_name": "Context",
                    "resource_url": "http://localhost:8001/guardian/management/contexts/app2/namespace/context2",
                }
            ],
        }

    @pytest.mark.asyncio
    async def test_get_contexts_for_namespace_name(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
        create_context,
    ):
        namespace_name = "namespace2"
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_namespace(session)
            await create_namespace(session, name=namespace_name)
            await create_context(session, name="context1")
            await create_context(
                session, name="context2", namespace_name=namespace_name
            )

        response = client.get(
            app.url_path_for(
                "get_contexts_by_namespace",
                namespace_name=namespace_name,
                app_name=DEFAULT_TEST_APP,
            )
        )
        assert response.status_code == 200
        assert response.json() == {
            "pagination": {"offset": 0, "limit": 1, "total_count": 1},
            "contexts": [
                {
                    "app_name": "app",
                    "namespace_name": "namespace2",
                    "name": "context2",
                    "display_name": "Context",
                    "resource_url": "http://localhost:8001/guardian/management/contexts/app/namespace2/context2",
                }
            ],
        }

    @pytest.mark.asyncio
    async def test_get_contexts_for_app_name_non_existent_app(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
        create_context,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_namespace(session)
            await create_context(session, name="context1")

        response = client.get(app.url_path_for("get_contexts_by_app", app_name="app2"))
        assert response.status_code == 200
        assert response.json() == {
            "pagination": {"offset": 0, "limit": 0, "total_count": 0},
            "contexts": [],
        }

    @pytest.mark.asyncio
    async def test_patch_context(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_namespace,
        create_context,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_namespace(session)
            await create_context(session)

        changed_display_name = "changed_display_name"
        response = client.patch(
            app.url_path_for(
                "edit_context",
                app_name=DEFAULT_TEST_APP,
                namespace_name=DEFAULT_TEST_NAMESPACE,
                name=DEFAULT_TEST_CONTEXT,
            ),
            json={"display_name": changed_display_name},
        )
        assert response.status_code == 201, response.json()
        assert response.json() == {
            "context": {
                "app_name": DEFAULT_TEST_APP,
                "namespace_name": DEFAULT_TEST_NAMESPACE,
                "name": DEFAULT_TEST_CONTEXT,
                "display_name": changed_display_name,
                "resource_url": f"{COMPLETE_URL}/contexts/{DEFAULT_TEST_APP}/"
                f"{DEFAULT_TEST_NAMESPACE}/{DEFAULT_TEST_CONTEXT}",
            }
        }

    @pytest.mark.asyncio
    async def test_patch_context_non_existing_context(
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
                "edit_context",
                app_name=DEFAULT_TEST_APP,
                namespace_name=DEFAULT_TEST_NAMESPACE,
                name=DEFAULT_TEST_CONTEXT,
            ),
            json={"display_name": changed_display_name},
        )
        assert response.status_code == 404, response.json()

    @pytest.mark.asyncio
    async def test_patch_context_non_existing_app(
        self,
        client,
    ):
        changed_display_name = "changed_display_name"
        response = client.patch(
            app.url_path_for(
                "edit_context",
                app_name=DEFAULT_TEST_APP,
                namespace_name=DEFAULT_TEST_NAMESPACE,
                name=DEFAULT_TEST_CONTEXT,
            ),
            json={"display_name": changed_display_name},
        )
        assert response.status_code == 404, response.json()

    @pytest.mark.asyncio
    async def test_patch_context_non_existing_namespace(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
        changed_display_name = "changed_display_name"
        response = client.patch(
            app.url_path_for(
                "edit_context",
                app_name=DEFAULT_TEST_APP,
                namespace_name=DEFAULT_TEST_NAMESPACE,
                name=DEFAULT_TEST_CONTEXT,
            ),
            json={"display_name": changed_display_name},
        )
        assert response.status_code == 404, response.json()
