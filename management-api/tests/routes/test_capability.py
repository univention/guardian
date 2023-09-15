# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import asdict
from urllib.parse import urljoin

import pytest
from guardian_management_api.adapters.capability import SQLCapabilityPersistenceAdapter
from guardian_management_api.adapters.role import SQLRolePersistenceAdapter
from guardian_management_api.constants import BASE_URL, COMPLETE_URL
from guardian_management_api.models.sql_persistence import DBCapability
from sqlalchemy import select
from sqlalchemy.sql.functions import count


@pytest.mark.e2e
class TestCapabilityEndpoints:
    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_capability(self, client, create_capabilities, sqlalchemy_mixin):
        async with sqlalchemy_mixin.session() as session:
            db_capability = (await create_capabilities(session, 1))[0]
        capability = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_capability)
        resource = client.app.url_path_for(
            "get_capability",
            app_name=capability.app_name,
            namespace_name=capability.namespace_name,
            name=capability.name,
        )
        response = client.get(resource)
        assert response.status_code == 200, response.json()
        permissions = [asdict(perm) for perm in capability.permissions]
        role = asdict(capability.role)
        del role["display_name"]
        for perm in permissions:
            del perm["display_name"]
        expected = {
            "capability": {
                "app_name": capability.app_name,
                "namespace_name": capability.namespace_name,
                "name": capability.name,
                "display_name": capability.display_name,
                "relation": "AND",
                "role": role,
                "permissions": permissions,
                "conditions": [asdict(cond) for cond in capability.conditions],
                "resource_url": f"{COMPLETE_URL}/capabilities/{capability.app_name}/"
                f"{capability.namespace_name}/{capability.name}",
            }
        }
        result_value = response.json()
        assert result_value == expected

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_capability_404(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_capability = (await create_capabilities(session, 1))[0]
        capability = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_capability)
        resource = client.app.url_path_for(
            "get_capability",
            app_name=capability.app_name,
            namespace_name="foo",
            name=capability.name,
        )
        response = client.get(resource)
        assert response.status_code == 404, response.json()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_capabilities(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_caps = await create_capabilities(session, 5)
        response = client.get(client.app.url_path_for("get_all_capabilities"))
        assert response.status_code == 200
        capabilities = response.json()["capabilities"]
        pagination = response.json()["pagination"]
        assert pagination == {"offset": 0, "limit": 5, "total_count": 5}
        for index, condition in enumerate(capabilities):
            orig_capability = SQLCapabilityPersistenceAdapter._db_cap_to_cap(
                db_caps[index]
            )
            permissions = [asdict(perm) for perm in orig_capability.permissions]
            role = asdict(orig_capability.role)
            del role["display_name"]
            for perm in permissions:
                del perm["display_name"]
            resource = client.app.url_path_for(
                "get_capability",
                app_name=orig_capability.app_name,
                namespace_name=orig_capability.namespace_name,
                name=orig_capability.name,
            )
            assert condition == {
                "app_name": orig_capability.app_name,
                "namespace_name": orig_capability.namespace_name,
                "name": orig_capability.name,
                "display_name": orig_capability.display_name,
                "resource_url": urljoin(BASE_URL, resource),
                "relation": "AND",
                "role": role,
                "permissions": permissions,
                "conditions": [asdict(cond) for cond in orig_capability.conditions],
            }

    @pytest.mark.asyncio
    async def test_get_capabilities_error(self, client):
        response = client.get(client.app.url_path_for("get_all_capabilities"))
        assert response.status_code == 500

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_capabilities_by_roles(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_caps = await create_capabilities(session, 10, 2)
        db_role1 = db_caps[0].role
        response = client.get(
            client.app.url_path_for(
                "get_capabilities_by_role",
                app_name=db_role1.namespace.app.name,
                namespace_name=db_role1.namespace.name,
                name=db_role1.name,
            )
        )
        assert response.status_code == 200
        capabilities = response.json()["capabilities"]
        pagination = response.json()["pagination"]
        assert pagination == {"offset": 0, "limit": 10, "total_count": 10}
        role = asdict(SQLRolePersistenceAdapter._db_role_to_role(db_role1))
        del role["display_name"]
        for index, condition in enumerate(capabilities):
            orig_capability = SQLCapabilityPersistenceAdapter._db_cap_to_cap(
                db_caps[index]
            )
            permissions = [asdict(perm) for perm in orig_capability.permissions]
            for perm in permissions:
                del perm["display_name"]
            resource = client.app.url_path_for(
                "get_capability",
                app_name=orig_capability.app_name,
                namespace_name=orig_capability.namespace_name,
                name=orig_capability.name,
            )
            assert condition == {
                "app_name": orig_capability.app_name,
                "namespace_name": orig_capability.namespace_name,
                "name": orig_capability.name,
                "display_name": orig_capability.display_name,
                "resource_url": urljoin(BASE_URL, resource),
                "relation": "AND",
                "role": role,
                "permissions": permissions,
                "conditions": [asdict(cond) for cond in orig_capability.conditions],
            }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_get_capabilities_by_namespaces(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_caps = await create_capabilities(session, 10, 2)
        db_cap1 = db_caps[0]
        response = client.get(
            client.app.url_path_for(
                "get_capabilities_by_namespace",
                app_name=db_cap1.namespace.app.name,
                namespace_name=db_cap1.namespace.name,
            )
        )
        assert response.status_code == 200
        pagination = response.json()["pagination"]
        assert pagination == {"offset": 0, "limit": 20, "total_count": 20}

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_capability(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_cap = (await create_capabilities(session, 1))[0]
        cap_to_create = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        cap_to_create.name = "my-cap"
        create_data = {
            "name": cap_to_create.name,
            "display_name": cap_to_create.display_name,
            "relation": cap_to_create.relation,
            "conditions": [
                {
                    "app_name": cond.app_name,
                    "namespace_name": cond.namespace_name,
                    "name": cond.name,
                    "parameters": [
                        {"name": param.name, "value": param.value}
                        for param in cond.parameters
                    ],
                }
                for cond in cap_to_create.conditions
            ],
            "permissions": [
                {
                    "app_name": perm.app_name,
                    "namespace_name": perm.namespace_name,
                    "name": perm.name,
                }
                for perm in cap_to_create.permissions
            ],
            "role": {
                "app_name": cap_to_create.role.app_name,
                "namespace_name": cap_to_create.role.namespace_name,
                "name": cap_to_create.role.name,
            },
        }
        result = client.post(
            client.app.url_path_for(
                "create_capability",
                app_name=cap_to_create.app_name,
                namespace_name=cap_to_create.namespace_name,
            ),
            json=create_data,
        )
        assert result.status_code == 200, result.json()
        permissions = [asdict(perm) for perm in cap_to_create.permissions]
        role = asdict(cap_to_create.role)
        del role["display_name"]
        for perm in permissions:
            del perm["display_name"]
        expected = {
            "capability": {
                "app_name": cap_to_create.app_name,
                "namespace_name": cap_to_create.namespace_name,
                "name": cap_to_create.name,
                "display_name": cap_to_create.display_name,
                "relation": "AND",
                "role": role,
                "permissions": permissions,
                "conditions": [asdict(cond) for cond in cap_to_create.conditions],
                "resource_url": f"{COMPLETE_URL}/capabilities/{cap_to_create.app_name}/"
                f"{cap_to_create.namespace_name}/{cap_to_create.name}",
            }
        }
        assert result.json() == expected

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_capability_role_not_found(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_cap = (await create_capabilities(session, 1))[0]
        cap_to_create = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        cap_to_create.name = "my-cap"
        create_data = {
            "name": cap_to_create.name,
            "display_name": cap_to_create.display_name,
            "relation": cap_to_create.relation,
            "conditions": [
                {
                    "app_name": cond.app_name,
                    "namespace_name": cond.namespace_name,
                    "name": cond.name,
                    "parameters": [
                        {"name": param.name, "value": param.value}
                        for param in cond.parameters
                    ],
                }
                for cond in cap_to_create.conditions
            ],
            "permissions": [
                {
                    "app_name": perm.app_name,
                    "namespace_name": perm.namespace_name,
                    "name": perm.name,
                }
                for perm in cap_to_create.permissions
            ],
            "role": {
                "app_name": cap_to_create.role.app_name,
                "namespace_name": "foo",
                "name": cap_to_create.role.name,
            },
        }
        result = client.post(
            client.app.url_path_for(
                "create_capability",
                app_name=cap_to_create.app_name,
                namespace_name=cap_to_create.namespace_name,
            ),
            json=create_data,
        )
        assert result.status_code == 400, result.json()
        assert result.json() == {
            "detail": {
                "message": "The role specified for the capability could not be found."
            }
        }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_capability_condition_not_found(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_cap = (await create_capabilities(session, 1))[0]
        cap_to_create = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        cap_to_create.name = "my-cap"
        create_data = {
            "name": cap_to_create.name,
            "display_name": cap_to_create.display_name,
            "relation": cap_to_create.relation,
            "conditions": [
                {
                    "app_name": "foo",
                    "namespace_name": cond.namespace_name,
                    "name": cond.name,
                    "parameters": [
                        {"name": param.name, "value": param.value}
                        for param in cond.parameters
                    ],
                }
                for cond in cap_to_create.conditions
            ],
            "permissions": [
                {
                    "app_name": perm.app_name,
                    "namespace_name": perm.namespace_name,
                    "name": perm.name,
                }
                for perm in cap_to_create.permissions
            ],
            "role": {
                "app_name": cap_to_create.role.app_name,
                "namespace_name": cap_to_create.role.namespace_name,
                "name": cap_to_create.role.name,
            },
        }
        result = client.post(
            client.app.url_path_for(
                "create_capability",
                app_name=cap_to_create.app_name,
                namespace_name=cap_to_create.namespace_name,
            ),
            json=create_data,
        )
        assert result.status_code == 400, result.json()
        assert result.json() == {
            "detail": {
                "message": "One or more conditions specified for the capability do not exist."
            }
        }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_capability_permission_not_found(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_cap = (await create_capabilities(session, 1))[0]
        cap_to_create = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        cap_to_create.name = "my-cap"
        create_data = {
            "name": cap_to_create.name,
            "display_name": cap_to_create.display_name,
            "relation": cap_to_create.relation,
            "conditions": [
                {
                    "app_name": cond.app_name,
                    "namespace_name": cond.namespace_name,
                    "name": cond.name,
                    "parameters": [
                        {"name": param.name, "value": param.value}
                        for param in cond.parameters
                    ],
                }
                for cond in cap_to_create.conditions
            ],
            "permissions": [
                {
                    "app_name": perm.app_name,
                    "namespace_name": perm.namespace_name,
                    "name": "foo",
                }
                for perm in cap_to_create.permissions
            ],
            "role": {
                "app_name": cap_to_create.role.app_name,
                "namespace_name": cap_to_create.role.namespace_name,
                "name": cap_to_create.role.name,
            },
        }
        result = client.post(
            client.app.url_path_for(
                "create_capability",
                app_name=cap_to_create.app_name,
                namespace_name=cap_to_create.namespace_name,
            ),
            json=create_data,
        )
        assert result.status_code == 400, result.json()
        assert result.json() == {
            "detail": {
                "message": "One or more permissions specified for the capability do not exist."
            }
        }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_capability_already_exists(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_cap = (await create_capabilities(session, 1))[0]
        cap_to_create = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        create_data = {
            "name": cap_to_create.name,
            "display_name": cap_to_create.display_name,
            "relation": cap_to_create.relation,
            "conditions": [
                {
                    "app_name": cond.app_name,
                    "namespace_name": cond.namespace_name,
                    "name": cond.name,
                    "parameters": [
                        {"name": param.name, "value": param.value}
                        for param in cond.parameters
                    ],
                }
                for cond in cap_to_create.conditions
            ],
            "permissions": [
                {
                    "app_name": perm.app_name,
                    "namespace_name": perm.namespace_name,
                    "name": perm.name,
                }
                for perm in cap_to_create.permissions
            ],
            "role": {
                "app_name": cap_to_create.role.app_name,
                "namespace_name": cap_to_create.role.namespace_name,
                "name": cap_to_create.role.name,
            },
        }
        result = client.post(
            client.app.url_path_for(
                "create_capability",
                app_name=cap_to_create.app_name,
                namespace_name=cap_to_create.namespace_name,
            ),
            json=create_data,
        )
        assert result.status_code == 400, result.json()
        assert result.json() == {
            "detail": {
                "message": "Capability with the same identifiers already exists."
            }
        }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_create_capability_parent_not_found(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_cap = (await create_capabilities(session, 1))[0]
        cap_to_create = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        cap_to_create.name = "other"
        create_data = {
            "name": cap_to_create.name,
            "display_name": cap_to_create.display_name,
            "relation": cap_to_create.relation,
            "conditions": [
                {
                    "app_name": cond.app_name,
                    "namespace_name": cond.namespace_name,
                    "name": cond.name,
                    "parameters": [
                        {"name": param.name, "value": param.value}
                        for param in cond.parameters
                    ],
                }
                for cond in cap_to_create.conditions
            ],
            "permissions": [
                {"app_name": perm.app_name, "namespace_name": "foo", "name": perm.name}
                for perm in cap_to_create.permissions
            ],
            "role": {
                "app_name": cap_to_create.role.app_name,
                "namespace_name": cap_to_create.role.namespace_name,
                "name": cap_to_create.role.name,
            },
        }
        result = client.post(
            client.app.url_path_for(
                "create_capability",
                app_name=cap_to_create.app_name,
                namespace_name="foo",
            ),
            json=create_data,
        )
        assert result.status_code == 400, result.json()
        assert result.json() == {
            "detail": {"message": "The app and or namespace does not exist."}
        }

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update_capability(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_cap = (await create_capabilities(session, 1))[0]
        cap_to_edit = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        edit_data = {
            "name": cap_to_edit.name,
            "display_name": "FOO",
            "relation": cap_to_edit.relation,
            "conditions": [],
            "permissions": [],
            "role": {
                "app_name": cap_to_edit.role.app_name,
                "namespace_name": cap_to_edit.role.namespace_name,
                "name": cap_to_edit.role.name,
            },
        }
        result = client.put(
            client.app.url_path_for(
                "update_capability",
                app_name=cap_to_edit.app_name,
                namespace_name=cap_to_edit.namespace_name,
                name=cap_to_edit.name,
            ),
            json=edit_data,
        )
        assert result.status_code == 200, result.json()
        role = asdict(cap_to_edit.role)
        del role["display_name"]
        expected = {
            "capability": {
                "app_name": cap_to_edit.app_name,
                "namespace_name": cap_to_edit.namespace_name,
                "name": cap_to_edit.name,
                "display_name": "FOO",
                "relation": "AND",
                "role": role,
                "permissions": [],
                "conditions": [],
                "resource_url": f"{COMPLETE_URL}/capabilities/{cap_to_edit.app_name}/"
                f"{cap_to_edit.namespace_name}/{cap_to_edit.name}",
            }
        }
        assert result.json() == expected

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_update_capability_404(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_cap = (await create_capabilities(session, 1))[0]
        cap_to_edit = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        edit_data = {
            "name": cap_to_edit.name,
            "display_name": "FOO",
            "relation": cap_to_edit.relation,
            "conditions": [],
            "permissions": [],
            "role": {
                "app_name": cap_to_edit.role.app_name,
                "namespace_name": cap_to_edit.role.namespace_name,
                "name": cap_to_edit.role.name,
            },
        }
        result = client.put(
            client.app.url_path_for(
                "update_capability",
                app_name=cap_to_edit.app_name,
                namespace_name="foo",
                name=cap_to_edit.name,
            ),
            json=edit_data,
        )
        assert result.status_code == 404, result.json()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_capability(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_cap = (await create_capabilities(session, 2))[0]
        cap_to_delete = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        result = client.delete(
            client.app.url_path_for(
                "delete_capability",
                app_name=cap_to_delete.app_name,
                namespace_name=cap_to_delete.namespace_name,
                name=cap_to_delete.name,
            )
        )
        assert result.status_code == 204, result.json()
        async with sqlalchemy_mixin.session() as session:
            assert (await session.scalar(select(count(DBCapability.id)))) == 1

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("create_tables")
    async def test_delete_capability_404(
        self, client, create_capabilities, sqlalchemy_mixin
    ):
        async with sqlalchemy_mixin.session() as session:
            db_cap = (await create_capabilities(session, 2))[0]
        cap_to_delete = SQLCapabilityPersistenceAdapter._db_cap_to_cap(db_cap)
        result = client.delete(
            client.app.url_path_for(
                "delete_capability",
                app_name=cap_to_delete.app_name,
                namespace_name="foo",
                name=cap_to_delete.name,
            )
        )
        assert result.status_code == 404, result.json()
