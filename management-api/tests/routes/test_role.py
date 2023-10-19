# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from urllib.parse import urljoin

import pytest
from guardian_management_api.adapters.role import SQLRolePersistenceAdapter
from guardian_management_api.constants import BASE_URL, COMPLETE_URL
from guardian_management_api.models.sql_persistence import DBRole


@pytest.mark.e2e
class TestRoleEndpoints:
    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_post_role(
        self,
        client,
        sqlalchemy_mixin,
        create_app,
        create_namespace,
    ):
        app_name = "test_app"
        namespace_name = "test_namespace"
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, name=app_name, display_name=None)
            await create_namespace(
                session, name=namespace_name, app_name=app_name, display_name=None
            )

        response = client.post(
            client.app.url_path_for(
                "create_role", app_name=app_name, namespace_name=namespace_name
            ),
            json={"name": "test_role", "display_name": "test_role_display_name"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "role": {
                "name": "test_role",
                "app_name": app_name,
                "namespace_name": namespace_name,
                "display_name": "test_role_display_name",
                "resource_url": f"{COMPLETE_URL}/roles/{app_name}/{namespace_name}/test_role",
            }
        }
        db_role = await sqlalchemy_mixin._get_single_object(
            DBRole,
            name="test_role",
            app_name=app_name,
            namespace_name=namespace_name,
        )

        assert db_role is not None

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_post_role_404_missing_namespace(
        self,
        client,
        sqlalchemy_mixin,
        create_app,
        create_namespace,
    ):
        app_name = "test_app"
        namespace_name = "test_namespace"
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, name=app_name, display_name=None)

        response = client.post(
            client.app.url_path_for(
                "create_role", app_name=app_name, namespace_name=namespace_name
            ),
            json={"name": "test_role", "display_name": "test_role_display_name"},
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": {
                "message": "The namespace of the object to be created does not exist."
            }
        }

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_post_role_404_missing_app(
        self,
        client,
        sqlalchemy_mixin,
        create_app,
        create_namespace,
    ):
        app_name = "test_app1"
        namespace_name = "test_namespace1"

        response = client.post(
            client.app.url_path_for(
                "create_role", app_name=app_name, namespace_name=namespace_name
            ),
            json={"name": "test_role", "display_name": "test_role_display_name"},
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": {"message": "The app of the object to be created does not exist."}
        }

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_edit_role(
        self, client, sqlalchemy_mixin, create_app, create_namespace, create_role
    ):
        app_name = "test_app"
        namespace_name = "test_namespace"
        name = "test_role"
        display_name = "test_role_display_name"
        new_display_name = f"{display_name}_new"
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, name=app_name, display_name=None)
            await create_namespace(
                session, name=namespace_name, app_name=app_name, display_name=None
            )
            await create_role(
                session,
                namespace_name=namespace_name,
                app_name=app_name,
                name=name,
                display_name=display_name,
            )

        response = client.patch(
            client.app.url_path_for(
                "edit_role",
                app_name=app_name,
                namespace_name=namespace_name,
                name="test_role",
            ),
            json={"display_name": new_display_name},
        )
        assert response.status_code == 200
        assert response.json()["role"] == {
            "name": name,
            "display_name": new_display_name,
            "namespace_name": namespace_name,
            "app_name": app_name,
            "resource_url": f"{COMPLETE_URL}/roles/{app_name}/{namespace_name}/{name}",
        }

        db_role = await sqlalchemy_mixin._get_single_object(
            DBRole,
            name="test_role",
            app_name=app_name,
            namespace_name=namespace_name,
        )

        assert db_role is not None
        assert db_role.display_name == new_display_name

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_edit_role_404(
        self, client, sqlalchemy_mixin, create_app, create_namespace, create_role
    ):
        app_name = "test_app"
        namespace_name = "test_namespace"
        display_name = "test_displayname"
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, name=app_name, display_name=None)
            await create_namespace(
                session, name=namespace_name, app_name=app_name, display_name=None
            )

        response = client.patch(
            client.app.url_path_for(
                "edit_role",
                app_name=app_name,
                namespace_name=namespace_name,
                name="test_role1",
            ),
            json={"display_name": display_name},
        )
        assert response.status_code == 404
        assert response.json() == {
            "detail": {
                "message": "No role with the identifier "
                "'test_app:test_namespace:test_role1' could be found."
            }
        }

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_get_role_fully_identified(
        self,
        client,
        sqlalchemy_mixin,
        create_app,
        create_namespace,
        create_role,
    ):
        app_name: str = "test_app"
        namespace_name: str = "test_namespace"
        role_name = "test_role"

        async with sqlalchemy_mixin.session() as session:
            await create_app(session, name=app_name, display_name=None)
            await create_namespace(
                session, name=namespace_name, app_name=app_name, display_name=None
            )
            await create_role(
                session=session,
                app_name=app_name,
                namespace_name=namespace_name,
                name=role_name,
                display_name="test_role_display_name",
            )

        response = client.get(
            client.app.url_path_for(
                "get_role",
                app_name=app_name,
                namespace_name=namespace_name,
                name=role_name,
            )
        )
        assert response.status_code == 200
        assert response.json() == {
            "role": {
                "name": "test_role",
                "app_name": app_name,
                "namespace_name": namespace_name,
                "display_name": "test_role_display_name",
                "resource_url": f"{COMPLETE_URL}/roles/{app_name}/{namespace_name}/test_role",
            }
        }

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_get_role_404(
        self,
        client,
        sqlalchemy_mixin,
        create_app,
        create_namespace,
        create_role,
    ):
        app_name: str = "test_app"
        namespace_name: str = "test_namespace"
        role_name = "test_role"

        async with sqlalchemy_mixin.session() as session:
            await create_app(session, name=app_name, display_name=None)
            await create_namespace(
                session, name=namespace_name, app_name=app_name, display_name=None
            )

        response = client.get(
            client.app.url_path_for(
                "get_role",
                app_name=app_name,
                namespace_name=namespace_name,
                name=role_name,
            )
        )
        assert response.status_code == 404

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_get_roles_by_app(
        self,
        client,
        create_role,
        sqlalchemy_mixin,
        create_app,
        create_namespace,
    ):
        app_names: list[str] = ["test_app" + str(i) for i in range(0, 2)]
        namespace_names: list[str] = ["test_namespace" + str(i) for i in range(0, 2)]
        role_names: list[str] = ["test_role" + str(i) for i in range(0, 2)]

        async with sqlalchemy_mixin.session() as session:
            for app_name, namespace_name, role_name in zip(
                app_names, namespace_names, role_names
            ):
                await create_app(session, name=app_name, display_name=None)
                await create_namespace(
                    session, name=namespace_name, app_name=app_name, display_name=None
                )
                await create_role(
                    session=session,
                    app_name=app_name,
                    namespace_name=namespace_name,
                    name=role_name,
                    display_name=role_name + "_display_name",
                )
        response = client.get(
            client.app.url_path_for(
                "get_roles_by_app",
                app_name=app_names[0],
            )
        )
        assert response.status_code == 200
        json_response = response.json()

        scoped_role = {
            "name": role_names[0],
            "app_name": app_names[0],
            "namespace_name": namespace_names[0],
            "display_name": role_names[0] + "_display_name",
            "resource_url": f"{COMPLETE_URL}/roles/{app_names[0]}/{namespace_names[0]}/{role_names[0]}",
        }

        unscoped_role = {
            "name": role_names[1],
            "app_name": app_names[1],
            "namespace_name": namespace_names[1],
            "display_name": role_names[1] + "_display_name",
            "resource_url": f"{COMPLETE_URL}/roles/{app_names[1]}/{namespace_names[1]}/{role_names[1]}",
        }

        assert json_response["pagination"] == {
            "offset": 0,
            "limit": 1,
            "total_count": 1,
        }
        assert len(json_response["roles"]) == 1
        assert json_response["roles"][0] == scoped_role
        assert json_response["roles"][0] != unscoped_role

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_get_roles_by_namespace(
        self,
        client,
        create_role,
        sqlalchemy_mixin,
        create_app,
        create_namespace,
    ):
        app_names: list[str] = ["test_app" + str(i) for i in range(0, 2)]
        namespace_names: list[str] = ["test_namespace" + str(i) for i in range(0, 2)]
        role_names: list[str] = ["test_role" + str(i) for i in range(0, 2)]

        async with sqlalchemy_mixin.session() as session:
            for app_name, namespace_name, role_name in zip(
                app_names, namespace_names, role_names
            ):
                await create_app(session, name=app_name, display_name=None)
                await create_namespace(
                    session, name=namespace_name, app_name=app_name, display_name=None
                )
                await create_role(
                    session=session,
                    app_name=app_name,
                    namespace_name=namespace_name,
                    name=role_name,
                    display_name=role_name + "_display_name",
                )
        response = client.get(
            client.app.url_path_for(
                "get_roles_by_namespace",
                app_name=app_names[0],
                namespace_name=namespace_names[0],
            )
        )
        assert response.status_code == 200
        json_response = response.json()

        scoped_role = {
            "name": role_names[0],
            "app_name": app_names[0],
            "namespace_name": namespace_names[0],
            "display_name": role_names[0] + "_display_name",
            "resource_url": f"{COMPLETE_URL}/roles/{app_names[0]}/{namespace_names[0]}/{role_names[0]}",
        }

        unscoped_role = {
            "name": role_names[1],
            "app_name": app_names[1],
            "namespace_name": namespace_names[1],
            "display_name": role_names[1] + "_display_name",
            "resource_url": f"{COMPLETE_URL}/roles/{app_names[1]}/{namespace_names[1]}/{role_names[1]}",
        }

        assert json_response["pagination"] == {
            "offset": 0,
            "limit": 1,
            "total_count": 1,
        }
        assert len(json_response["roles"]) == 1
        assert json_response["roles"][0] == scoped_role
        assert json_response["roles"][0] != unscoped_role

    @pytest.mark.usefixtures("create_tables")
    @pytest.mark.asyncio
    async def test_get_roles_unscoped(
        self,
        client,
        create_role,
        sqlalchemy_mixin,
        create_app,
        create_namespace,
    ):
        app_names: list[str] = ["test_app" + str(i) for i in range(0, 2)]
        namespace_names: list[str] = ["test_namespace" + str(i) for i in range(0, 2)]
        role_names: list[str] = ["test_role" + str(i) for i in range(0, 2)]

        async with sqlalchemy_mixin.session() as session:
            for app_name, namespace_name, role_name in zip(
                app_names, namespace_names, role_names
            ):
                await create_app(session, name=app_name, display_name=None)
                await create_namespace(
                    session, name=namespace_name, app_name=app_name, display_name=None
                )
                await create_role(
                    session=session,
                    app_name=app_name,
                    namespace_name=namespace_name,
                    name=role_name,
                    display_name=role_name + "_display_name",
                )
        response = client.get(
            client.app.url_path_for(
                "get_all_roles",
            )
        )
        assert response.status_code == 200
        json_response = response.json()

        scoped_roles = [
            {
                "name": role_names[0],
                "app_name": app_names[0],
                "namespace_name": namespace_names[0],
                "display_name": role_names[0] + "_display_name",
                "resource_url": (
                    f"{COMPLETE_URL}/roles/{app_names[0]}"
                    f"/{namespace_names[0]}/{role_names[0]}"
                ),
            },
            {
                "name": role_names[1],
                "app_name": app_names[1],
                "namespace_name": namespace_names[1],
                "display_name": role_names[1] + "_display_name",
                "resource_url": (
                    f"{COMPLETE_URL}/roles/{app_names[1]}"
                    f"/{namespace_names[1]}/{role_names[1]}"
                ),
            },
        ]

        assert json_response["pagination"] == {
            "offset": 0,
            "limit": 2,
            "total_count": 2,
        }
        assert len(json_response["roles"]) == 2
        for i in range(0, 2):
            assert json_response["roles"][i] == scoped_roles[i]

    @pytest.mark.asyncio
    # @pytest.mark.usefixtures("create_tables")
    async def test_get_roles_500(self, client):
        response = client.get(client.app.url_path_for("get_all_roles"))
        assert response.status_code == 500

    @pytest.mark.parametrize(
        "offset,limit", [(0, None), (1, None), (0, None), (0, 3), (0, 20)]
    )
    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_roles_pagination(
        self, client, create_roles, sqlalchemy_mixin, offset, limit
    ):
        async with sqlalchemy_mixin.session() as session:
            db_roles = await create_roles(session, 10)
        params = {"offset": offset}
        if limit:
            params["limit"] = limit
        response = client.get(client.app.url_path_for("get_all_roles"), params=params)
        assert response.status_code == 200, response.json()
        roles = response.json()["roles"]
        pagination = response.json()["pagination"]
        assert pagination == {
            "offset": offset,
            "limit": 10 if limit is None else limit,
            "total_count": 10,
        }
        for index, role in enumerate(roles):
            orig_role = SQLRolePersistenceAdapter._db_role_to_role(
                db_roles[offset + index]
            )
            resource = client.app.url_path_for(
                "get_role",
                app_name=orig_role.app_name,
                namespace_name=orig_role.namespace_name,
                name=orig_role.name,
            )

            assert role == {
                "app_name": orig_role.app_name,
                "namespace_name": orig_role.namespace_name,
                "name": orig_role.name,
                "display_name": orig_role.display_name,
                "resource_url": urljoin(BASE_URL, resource),
            }
