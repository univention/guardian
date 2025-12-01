from dataclasses import asdict
from urllib.parse import urljoin

import pytest
from guardian_management_api.adapters.permission import SQLPermissionPersistenceAdapter
from guardian_management_api.constants import BASE_URL, COMPLETE_URL
from guardian_management_api.main import app
from guardian_management_api.models.permission import Permission
from guardian_management_api.models.sql_persistence import DBPermission
from sqlalchemy import select


@pytest.mark.e2e
class TestPermissionEndpoints:
    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_permission(self, client, create_permissions, sqlalchemy_mixin):
        async with sqlalchemy_mixin.session() as session:
            db_permission = (await create_permissions(session, 1))[0]
        permission = SQLPermissionPersistenceAdapter._db_permission_to_permission(
            db_permission
        )
        resource = client.app.url_path_for(
            "get_permission",
            app_name=permission.app_name,
            namespace_name=permission.namespace_name,
            name=permission.name,
        )
        response = client.get(resource)
        assert response.status_code == 200
        assert response.json() == {
            "permission": {
                "app_name": permission.app_name,
                "namespace_name": permission.namespace_name,
                "name": permission.name,
                "display_name": permission.display_name,
                "resource_url": urljoin(BASE_URL, resource),
            }
        }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_permission_404(self, client):
        resource = client.app.url_path_for(
            "get_permission",
            app_name="app",
            namespace_name="namespace",
            name="permission",
        )
        response = client.get(resource)
        assert response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_permissions(self, client, create_permissions, sqlalchemy_mixin):
        async with sqlalchemy_mixin.session() as session:
            db_permissions = await create_permissions(session, 5)
        response = client.get(client.app.url_path_for("get_all_permissions"))
        assert response.status_code == 200
        permissions = response.json()["permissions"]
        pagination = response.json()["pagination"]
        assert pagination == {"offset": 0, "limit": 5, "total_count": 5}
        for index, permission in enumerate(permissions):
            orig_permission = (
                SQLPermissionPersistenceAdapter._db_permission_to_permission(
                    db_permissions[index]
                )
            )
            resource = client.app.url_path_for(
                "get_permission",
                app_name=orig_permission.app_name,
                namespace_name=orig_permission.namespace_name,
                name=orig_permission.name,
            )
            assert permission == {
                "app_name": orig_permission.app_name,
                "namespace_name": orig_permission.namespace_name,
                "name": orig_permission.name,
                "display_name": orig_permission.display_name,
                "resource_url": urljoin(BASE_URL, resource),
            }

    @pytest.mark.parametrize(
        "offset,limit", [(0, None), (1, None), (0, None), (0, 3), (0, 20)]
    )
    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_permissions_pagination(
        self, client, create_permissions, sqlalchemy_mixin, offset, limit
    ):
        async with sqlalchemy_mixin.session() as session:
            db_permissions = await create_permissions(session, 10)
        params = {"offset": offset}
        if limit:
            params["limit"] = limit
        response = client.get(
            client.app.url_path_for("get_all_permissions"), params=params
        )
        assert response.status_code == 200, response.json()
        permissions = response.json()["permissions"]
        pagination = response.json()["pagination"]
        assert pagination == {
            "offset": offset,
            "limit": 10 if limit is None else limit,
            "total_count": 10,
        }
        for index, permission in enumerate(permissions):
            orig_permission = (
                SQLPermissionPersistenceAdapter._db_permission_to_permission(
                    db_permissions[offset + index]
                )
            )
            resource = client.app.url_path_for(
                "get_permission",
                app_name=orig_permission.app_name,
                namespace_name=orig_permission.namespace_name,
                name=orig_permission.name,
            )
            assert permission == {
                "app_name": orig_permission.app_name,
                "namespace_name": orig_permission.namespace_name,
                "name": orig_permission.name,
                "display_name": orig_permission.display_name,
                "resource_url": urljoin(BASE_URL, resource),
            }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("drop_tables")
    async def test_get_permissions_error(self, client):
        response = client.get(client.app.url_path_for("get_all_permissions"))
        assert response.status_code == 500

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_permission(self, client, sqlalchemy_mixin, create_namespaces):
        async with sqlalchemy_mixin.session() as session:
            namespace = (await create_namespaces(session, 1))[0]
        permission_to_create = Permission(
            app_name=namespace.app.name,
            namespace_name=namespace.name,
            name="permission",
            display_name="Permission",
        )
        result = client.post(
            client.app.url_path_for(
                "create_permission",
                app_name=permission_to_create.app_name,
                namespace_name=permission_to_create.namespace_name,
            ),
            json={
                "name": permission_to_create.name,
                "display_name": permission_to_create.display_name,
            },
        )
        assert result.status_code == 201, result.json()
        expected_result = asdict(permission_to_create)
        expected_result["resource_url"] = (
            f"{COMPLETE_URL}/permissions/{permission_to_create.app_name}/"
            f"{permission_to_create.namespace_name}/{permission_to_create.name}"
        )
        assert result.json()["permission"] == expected_result
        db_permission = await sqlalchemy_mixin._get_single_object(
            DBPermission,
            name=permission_to_create.name,
            app_name=permission_to_create.app_name,
            namespace_name=namespace.name,
        )
        for attribute in ("name", "display_name"):
            assert getattr(db_permission, attribute) == getattr(
                permission_to_create, attribute
            )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_permission_unknown_parents(self, client):
        permission_to_create = Permission(
            app_name="some_app",
            namespace_name="some_namespace",
            name="permission",
            display_name="Permission",
        )
        result = client.post(
            client.app.url_path_for(
                "create_permission",
                app_name=permission_to_create.app_name,
                namespace_name=permission_to_create.namespace_name,
            ),
            json={
                "name": permission_to_create.name,
                "display_name": permission_to_create.display_name,
            },
        )
        assert result.status_code == 404, result.json()
        assert result.json() == {
            "detail": {"message": "The app of the object to be created does not exist."}
        }, result.json()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_permission_already_exists(
        self, client, sqlalchemy_mixin, create_permissions
    ):
        async with sqlalchemy_mixin.session() as session:
            db_permission = (await create_permissions(session, 1))[0]
        permission_to_create = Permission(
            app_name=db_permission.namespace.app.name,
            namespace_name=db_permission.namespace.name,
            name=db_permission.name,
            display_name="Permission",
        )
        result = client.post(
            client.app.url_path_for(
                "create_permission",
                app_name=permission_to_create.app_name,
                namespace_name=permission_to_create.namespace_name,
            ),
            json={
                "name": permission_to_create.name,
                "display_name": permission_to_create.display_name,
            },
        )
        assert result.status_code == 400, result.json()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_edit_permission(self, client, sqlalchemy_mixin, create_permissions):
        async with sqlalchemy_mixin.session() as session:
            db_permission = (await create_permissions(session, 1))[0]
        new_values = {"display_name": "NEW DISPLAY NAME"}
        result = client.patch(
            client.app.url_path_for(
                "edit_permission",
                app_name=db_permission.namespace.app.name,
                namespace_name=db_permission.namespace.name,
                name=db_permission.name,
            ),
            json=new_values,
        )
        assert result.status_code == 200, result.json()
        result_data = result.json()
        for key, value in new_values.items():
            assert result_data["permission"][key] == value, result_data

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("drop_tables")
    async def test_edit_permission_error(self, client):
        new_values = {"display_name": "NEW DISPLAY NAME"}
        result = client.patch(
            client.app.url_path_for(
                "edit_permission",
                app_name="app",
                namespace_name="namespace",
                name="permission",
            ),
            json=new_values,
        )
        assert result.status_code == 500, result.json()


@pytest.mark.e2e
@pytest.mark.e2e_udm
class TestPermissionEndpointsAuthorization:
    @pytest.mark.asyncio
    async def test_get_guardian_permission_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        create_permission,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="guardian", display_name=None)
            await create_namespace(
                session=session,
                name="namespace",
                display_name=None,
                app_name="guardian",
            )
            await create_permission(
                session=session,
                name="test",
                display_name=None,
                app_name="guardian",
                namespace_name="namespace",
            )
        response = client.get(
            app.url_path_for(
                "get_permission",
                name="test",
                namespace_name="namespace",
                app_name="guardian",
            ),
        )
        assert response.status_code == 200
        assert response.json()["permission"]["name"] == "test"

    @pytest.mark.asyncio
    async def test_get_other_permission_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        create_permission,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="other", display_name=None)
            await create_namespace(
                session=session,
                name="namespace",
                display_name=None,
                app_name="other",
            )
            await create_permission(
                session=session,
                name="test",
                display_name=None,
                app_name="other",
                namespace_name="namespace",
            )
        response = client.get(
            app.url_path_for(
                "get_permission",
                name="test",
                namespace_name="namespace",
                app_name="other",
            ),
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_edit_guardian_permission_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        create_permission,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="guardian", display_name=None)
            await create_namespace(
                session=session,
                name="namespace",
                display_name=None,
                app_name="guardian",
            )
            await create_permission(
                session=session,
                name="test",
                display_name=None,
                app_name="guardian",
                namespace_name="namespace",
            )
        response = client.patch(
            app.url_path_for(
                "edit_permission",
                name="test",
                namespace_name="namespace",
                app_name="guardian",
            ),
            json={
                "name": "test",
                "display_name": "expected displayname",
                "permissions": [],
                "relation": "AND",
                "permission": {
                    "app_name": "guardian",
                    "namespace_name": "namespace",
                    "name": "permission",
                },
            },
        )
        assert response.status_code == 200
        assert response.json()["permission"]["display_name"] == "expected displayname"

    @pytest.mark.asyncio
    async def test_edit_other_permission_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        create_permission,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="other", display_name=None)
            await create_namespace(
                session=session,
                name="namespace",
                display_name=None,
                app_name="other",
            )
            await create_permission(
                session=session,
                name="test",
                display_name=None,
                app_name="other",
                namespace_name="namespace",
            )
        response = client.patch(
            app.url_path_for(
                "edit_permission",
                name="test",
                namespace_name="namespace",
                app_name="other",
            ),
            json={
                "name": "test",
                "display_name": "expected displayname",
                "permissions": [],
                "relation": "AND",
                "permission": {
                    "app_name": "other",
                    "namespace_name": "namespace",
                    "name": "permission",
                },
            },
        )
        assert response.status_code == 403

        async with sqlalchemy_mixin.session() as session:
            db_cap = (
                (await session.execute(select(DBPermission).filter_by(name="test")))
                .unique()
                .scalar_one_or_none()
            )
            assert db_cap is not None
            assert db_cap.display_name != "expected displayname"

    @pytest.mark.asyncio
    async def test_get_all_permissions(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        create_permission,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="guardian", display_name=None)
            await create_namespace(
                session=session,
                name="namespace",
                display_name=None,
                app_name="guardian",
            )
            await create_permission(
                session=session,
                name="test",
                display_name=None,
                app_name="guardian",
                namespace_name="namespace",
            )
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="other", display_name=None)
            await create_namespace(
                session=session,
                name="namespace",
                display_name=None,
                app_name="other",
            )
            await create_permission(
                session=session,
                name="test",
                display_name=None,
                app_name="other",
                namespace_name="namespace",
            )
        response = client.get(
            app.url_path_for("get_all_permissions"),
        )
        assert response.status_code == 200
        assert any(
            permission["name"] == "test"
            for permission in response.json()["permissions"]
        )
        assert not any(
            permission["name"] == "other"
            for permission in response.json()["permissions"]
        )

    @pytest.mark.asyncio
    async def test_create_permission_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        create_permission,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="other", display_name=None)
            await create_namespace(
                session=session,
                name="namespace",
                display_name=None,
                app_name="other",
            )
        response = client.post(
            app.url_path_for(
                "create_permission", namespace_name="namespace", app_name="other"
            ),
            json={
                "name": "test3",
                "display_name": "expected displayname",
                "permissions": [],
                "relation": "AND",
                "permission": {
                    "app_name": "other",
                    "namespace_name": "namespace",
                    "name": "permission",
                },
            },
        )
        assert response.status_code == 403

        # check that the permission was not created in the database
        async with sqlalchemy_mixin.session() as session:
            db_cap = (
                (await session.execute(select(DBPermission).filter_by(name="test3")))
                .unique()
                .scalar_one_or_none()
            )
            assert db_cap is None

    # get permissions by app
    @pytest.mark.asyncio
    async def test_get_permissions_by_app_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        create_permission,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="guardian", display_name=None)
            await create_namespace(
                session=session,
                name="namespace",
                display_name=None,
                app_name="guardian",
            )
            await create_permission(
                session=session,
                name="test",
                display_name=None,
                app_name="guardian",
                namespace_name="namespace",
            )
        response = client.get(
            app.url_path_for("get_permissions_by_app", app_name="guardian"),
        )
        assert response.status_code == 200
        assert any(
            permission["name"] == "test"
            for permission in response.json()["permissions"]
        )

    @pytest.mark.asyncio
    async def test_get_permissions_by_app_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        create_permission,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="other", display_name=None)
            await create_namespace(
                session=session,
                name="namespace",
                display_name=None,
                app_name="other",
            )
            await create_permission(
                session=session,
                name="test",
                display_name=None,
                app_name="other",
                namespace_name="namespace",
            )
        response = client.get(
            app.url_path_for("get_permissions_by_app", app_name="other"),
        )
        assert response.json()["permissions"] == []

    @pytest.mark.asyncio
    async def test_get_permissions_by_namespace_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        create_permission,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="guardian", display_name=None)
            await create_namespace(
                session=session,
                name="namespace",
                display_name=None,
                app_name="guardian",
            )
            await create_permission(
                session=session,
                name="test",
                display_name=None,
                app_name="guardian",
                namespace_name="namespace",
            )
        response = client.get(
            app.url_path_for(
                "get_permissions_by_namespace",
                app_name="guardian",
                namespace_name="namespace",
            ),
        )
        assert response.status_code == 200
        assert any(
            permission["name"] == "test"
            for permission in response.json()["permissions"]
        )

    @pytest.mark.asyncio
    async def test_get_permissions_by_namespace_not_allowed(
        self,
        client,
        create_tables,
        create_app,
        create_namespace,
        create_permission,
        sqlalchemy_mixin,
        set_up_auth,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session=session, name="other", display_name=None)
            await create_namespace(
                session=session,
                name="namespace",
                display_name=None,
                app_name="other",
            )
            await create_permission(
                session=session,
                name="test",
                display_name=None,
                app_name="other",
                namespace_name="namespace",
            )
        response = client.get(
            app.url_path_for(
                "get_permissions_by_namespace",
                app_name="other",
                namespace_name="namespace",
            ),
        )
        assert response.json()["permissions"] == []
