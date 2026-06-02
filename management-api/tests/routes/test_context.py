# Copyright (C) 2023-2026 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


import pytest
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.main import app
from guardian_management_api.models.sql_persistence import DBContext
from sqlalchemy import select
from sqlalchemy.sql.functions import count

DEFAULT_TEST_APP = "app"
DEFAULT_TEST_CONTEXT = "context"


@pytest.mark.usefixtures("create_tables")
class TestContextEndpoints:
    @pytest.mark.asyncio
    async def test_post(
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
            ),
            json={
                "name": context_name,
                "display_name": "test",
            },
        )
        assert response.status_code == 201, response.json()
        assert response.json() == {
            "context": {
                "app_name": DEFAULT_TEST_APP,
                "name": context_name,
                "display_name": "test",
                "resource_url": f"{COMPLETE_URL}/contexts/{DEFAULT_TEST_APP}"
                f"/{context_name}",
            }
        }

    @pytest.mark.asyncio
    async def test_post_409_exists(
        self,
        client,
        create_app,
        create_context,
        sqlalchemy_mixin,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_context(session)
        response = client.post(
            app.url_path_for(
                "create_context",
                app_name=DEFAULT_TEST_APP,
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
        create_context,
        base_url,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_context(session)
        response = client.get(
            app.url_path_for(
                "get_context",
                app_name=DEFAULT_TEST_APP,
                name=DEFAULT_TEST_CONTEXT,
            ),
        )
        assert response.status_code == 200, response.json()
        assert response.json() == {
            "context": {
                "app_name": DEFAULT_TEST_APP,
                "display_name": "Context",
                "name": DEFAULT_TEST_CONTEXT,
                "resource_url": f"{base_url}/guardian/management/contexts/"
                f"{DEFAULT_TEST_APP}/{DEFAULT_TEST_CONTEXT}",
            }
        }

    @pytest.mark.asyncio
    async def test_get_context_non_existing_raises_404(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
        response = client.get(
            app.url_path_for(
                "get_context",
                app_name=DEFAULT_TEST_APP,
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
        create_context,
        base_url,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_context(session, name="context1")
            await create_context(session, name="context2")

        response = client.get(app.url_path_for("get_all_contexts"))
        assert response.status_code == 200
        assert response.json() == {
            "pagination": {"offset": 0, "limit": 2, "total_count": 2},
            "contexts": [
                {
                    "app_name": "app",
                    "name": "context1",
                    "display_name": "Context",
                    "resource_url": f"{base_url}/guardian/management/contexts/app/context1",
                },
                {
                    "app_name": "app",
                    "name": "context2",
                    "display_name": "Context",
                    "resource_url": f"{base_url}/guardian/management/contexts/app/context2",
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_get_contexts_for_app_name(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_context,
        base_url,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_app(session, name="app2")
            await create_context(session, name="context1")
            await create_context(session, name="context2", app_name="app2")

        response = client.get(app.url_path_for("get_contexts_by_app", app_name="app2"))
        assert response.status_code == 200
        assert response.json() == {
            "pagination": {"offset": 0, "limit": 1, "total_count": 1},
            "contexts": [
                {
                    "app_name": "app2",
                    "name": "context2",
                    "display_name": "Context",
                    "resource_url": f"{base_url}/guardian/management/contexts/app2/context2",
                }
            ],
        }

    @pytest.mark.asyncio
    async def test_get_contexts_for_app_name_non_existent_app(
        self,
        client,
        create_app,
        sqlalchemy_mixin,
        create_context,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
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
        create_context,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session)
            await create_context(session)

        changed_display_name = "changed_display_name"
        response = client.patch(
            app.url_path_for(
                "edit_context",
                app_name=DEFAULT_TEST_APP,
                name=DEFAULT_TEST_CONTEXT,
            ),
            json={"display_name": changed_display_name},
        )
        assert response.status_code == 200, response.json()
        assert response.json() == {
            "context": {
                "app_name": DEFAULT_TEST_APP,
                "name": DEFAULT_TEST_CONTEXT,
                "display_name": changed_display_name,
                "resource_url": f"{COMPLETE_URL}/contexts/{DEFAULT_TEST_APP}/"
                f"{DEFAULT_TEST_CONTEXT}",
            }
        }

    @pytest.mark.asyncio
    async def test_patch_context_non_existing_context(
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
                name=DEFAULT_TEST_CONTEXT,
            ),
            json={"display_name": changed_display_name},
        )
        assert response.status_code == 404, response.json()

    @pytest.mark.asyncio
    async def test_delete_context(self, client, create_contexts, sqlalchemy_mixin):
        async with sqlalchemy_mixin.session() as session:
            db_contexts = await create_contexts(session, 2)
            target = db_contexts[0]
            app_name = target.app.name
            name = target.name
        result = client.delete(
            client.app.url_path_for(
                "delete_context",
                app_name=app_name,
                name=name,
            )
        )
        assert result.status_code == 204, result.text
        async with sqlalchemy_mixin.session() as session:
            assert (await session.scalar(select(count(DBContext.id)))) == 1

    @pytest.mark.asyncio
    async def test_delete_context_404(self, client):
        result = client.delete(
            client.app.url_path_for(
                "delete_context",
                app_name=DEFAULT_TEST_APP,
                name=DEFAULT_TEST_CONTEXT,
            )
        )
        assert result.status_code == 404, result.json()


@pytest.mark.e2e
@pytest.mark.e2e_udm
class TestContextEndpointsAuthorization:
    @pytest.mark.asyncio
    async def test_get_guardian_context_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_context,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="guardian", display_name=None)
            await create_context(
                session=session,
                name="test",
                display_name=None,
                app_name="guardian",
            )
        response = client.get(
            app.url_path_for(
                "get_context",
                name="test",
                app_name="guardian",
            ),
        )
        assert response.status_code == 200
        assert response.json()["context"]["name"] == "test"

    @pytest.mark.asyncio
    async def test_get_other_context_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_context,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="other", display_name=None)
            await create_context(
                session=session,
                name="test",
                display_name=None,
                app_name="other",
            )
        response = client.get(
            app.url_path_for(
                "get_context",
                name="test",
                app_name="other",
            ),
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_edit_guardian_context_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_context,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="guardian", display_name=None)
            await create_context(
                session=session,
                name="test",
                display_name=None,
                app_name="guardian",
            )
        response = client.patch(
            app.url_path_for(
                "edit_context",
                name="test",
                app_name="guardian",
            ),
            json={
                "name": "test",
                "display_name": "expected displayname",
                "permissions": [],
                "contexts": [],
                "relation": "AND",
                "context": {
                    "app_name": "guardian",
                    "name": "context",
                },
            },
        )
        assert response.status_code == 200
        assert response.json()["context"]["display_name"] == "expected displayname"

    @pytest.mark.asyncio
    async def test_edit_other_context_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_context,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="other", display_name=None)
            await create_context(
                session=session,
                name="test",
                display_name=None,
                app_name="other",
            )
        response = client.patch(
            app.url_path_for(
                "edit_context",
                name="test",
                app_name="other",
            ),
            json={
                "name": "test",
                "display_name": "expected displayname",
                "permissions": [],
                "contexts": [],
                "relation": "AND",
                "context": {
                    "app_name": "other",
                    "name": "context",
                },
            },
        )
        assert response.status_code == 403

        async with sqlalchemy_mixin.session() as session:
            db_cap = (
                (await session.execute(select(DBContext).filter_by(name="test")))
                .unique()
                .scalar_one_or_none()
            )
            assert db_cap is not None
            assert db_cap.display_name != "expected displayname"

    @pytest.mark.asyncio
    async def test_get_all_contexts(
        self,
        client,
        create_tables,
        create_app,
        create_context,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="guardian", display_name=None)
            await create_context(
                session=session,
                name="test",
                display_name=None,
                app_name="guardian",
            )
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="other", display_name=None)
            await create_context(
                session=session,
                name="test",
                display_name=None,
                app_name="other",
            )
        response = client.get(
            app.url_path_for("get_all_contexts"),
        )
        assert response.status_code == 200
        assert any(context["name"] == "test" for context in response.json()["contexts"])
        assert not any(
            context["name"] == "other" for context in response.json()["contexts"]
        )

    @pytest.mark.asyncio
    async def test_create_context_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_context,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="other", display_name=None)
        response = client.post(
            app.url_path_for("create_context", app_name="other"),
            json={
                "name": "test3",
                "display_name": "expected displayname",
                "permissions": [],
                "contexts": [],
                "relation": "AND",
                "context": {
                    "app_name": "other",
                    "name": "context",
                },
            },
        )
        assert response.status_code == 403

        # check that the context was not created in the database
        async with sqlalchemy_mixin.session() as session:
            db_cap = (
                (await session.execute(select(DBContext).filter_by(name="test3")))
                .unique()
                .scalar_one_or_none()
            )
            assert db_cap is None

    # get contexts by app
    @pytest.mark.asyncio
    async def test_get_contexts_by_app_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_context,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="guardian", display_name=None)
            await create_context(
                session=session,
                name="test",
                display_name=None,
                app_name="guardian",
            )
        response = client.get(
            app.url_path_for("get_contexts_by_app", app_name="guardian"),
        )
        assert response.status_code == 200
        assert any(context["name"] == "test" for context in response.json()["contexts"])

    @pytest.mark.asyncio
    async def test_get_contexts_by_app_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_context,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="other", display_name=None)
            await create_context(
                session=session,
                name="test",
                display_name=None,
                app_name="other",
            )
        response = client.get(
            app.url_path_for("get_contexts_by_app", app_name="other"),
        )
        assert response.json()["contexts"] == []

    @pytest.mark.asyncio
    async def test_delete_other_context_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_context,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="other", display_name=None)
            await create_context(
                session=session,
                name="test",
                display_name=None,
                app_name="other",
            )
        response = client.delete(
            app.url_path_for(
                "delete_context",
                name="test",
                app_name="other",
            ),
        )
        assert response.status_code == 403, response.json()

        async with sqlalchemy_mixin.session() as session:
            db_context = (
                (await session.execute(select(DBContext).filter_by(name="test")))
                .unique()
                .scalar_one_or_none()
            )
            assert db_context is not None
