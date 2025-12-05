# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from unittest.mock import patch

import pytest
from guardian_authorization_api.errors import PersistenceError

from ..conftest import get_authz_permissions_check_request_dict, opa_is_running
from ..mock_classes import MockUDMModule, MockUdmObject


class TestPermissionsCheckUnittest:
    @pytest.mark.asyncio
    async def test_permissions_check_opa_errors(self, client, opa_async_mock):
        opa_async_mock.return_value = 1
        data = get_authz_permissions_check_request_dict()
        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 500, response.json()
        assert response.json() == {
            "detail": {
                "message": "Upstream returned faulty data for check_permissions."
            }
        }

        opa_async_mock.side_effect = Exception("Testexception")

        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 500, response.json()
        assert response.json() == {
            "detail": {"message": "Upstream error while checking targeted permissions."}
        }

        data["targeted_permissions_to_check"] = []
        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 500, response.json()
        assert response.json() == {
            "detail": {"message": "Upstream error while checking general permissions."}
        }

    @pytest.mark.asyncio
    async def test_permissions_check_minimal(self, client, opa_async_mock):
        data = {
            "actor": {
                "id": "actor-1",
                "roles": [
                    {
                        "app_name": "app1",
                        "namespace_name": "namespace1",
                        "name": "role1",
                    },
                ],
                "attributes": {},
            },
            "general_permissions_to_check": [
                {"app_name": "app1", "namespace_name": "ns1", "name": "ps1"}
            ],
            "targeted_permissions_to_check": [
                {"app_name": "app1", "namespace_name": "ns1", "name": "ps2"}
            ],
            "extra_request_data": {},
        }

        opa_async_mock.return_value = [
            {"target_id": "", "result": True},
            {"target_id": "id1", "result": False},
            {"target_id": "id2", "result": True},
        ]

        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 200, response.json()

        assert response.json() == {
            "actor_id": "actor-1",
            "permissions_check_results": [
                {"target_id": "id1", "actor_has_permissions": False},
                {"target_id": "id2", "actor_has_permissions": True},
            ],
            "actor_has_all_general_permissions": True,
            "actor_has_all_targeted_permissions": False,
        }

    @pytest.mark.asyncio
    async def test_permissions_check_full(
        self,
        client,
        opa_async_mock,
    ):
        data = get_authz_permissions_check_request_dict()
        opa_async_mock.return_value = [
            {"target_id": "", "result": True},
            {"target_id": "id1", "result": False},
            {"target_id": "id2", "result": True},
        ]

        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 200, response.json()

        assert response.json() == {
            "actor_id": data["actor"]["id"],
            "permissions_check_results": [
                {"target_id": "id1", "actor_has_permissions": False},
                {"target_id": "id2", "actor_has_permissions": True},
            ],
            "actor_has_all_general_permissions": True,
            "actor_has_all_targeted_permissions": False,
        }

    @pytest.mark.asyncio
    async def test_check_permissions_with_lookup(
        self, client, udm_mock, opa_async_mock
    ):
        data = get_authz_permissions_check_request_dict(n_actor_roles=0, n_targets=1)
        actor_id = "actor-id"
        target_id = "uid=target-id"
        data["actor"] = {"id": actor_id}
        data["targets"][0]["old_target"] = {"id": target_id}
        data["targets"][0]["new_target"]["id"] = target_id
        opa_async_mock.return_value = [
            {"target_id": "", "result": True},
            {"target_id": target_id, "result": False},
        ]
        users = {
            target_id: MockUdmObject(
                dn=target_id, properties={"guardianRoles": ["ucsschool:users:student"]}
            ),
            actor_id: MockUdmObject(
                dn=actor_id, properties={"guardianRoles": ["ucsschool:users:teacher"]}
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("check_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()
        assert response.json() == {
            "actor_id": "actor-id",
            "permissions_check_results": [
                {"target_id": target_id, "actor_has_permissions": False},
            ],
            "actor_has_all_general_permissions": True,
            "actor_has_all_targeted_permissions": False,
        }

    @pytest.mark.asyncio
    async def test_check_permissions_with_lookup_partial(
        self, client, udm_mock, opa_async_mock
    ):
        data = get_authz_permissions_check_request_dict(n_actor_roles=0, n_targets=2)
        actor_id = "actor-id"
        target_lookup_id = "uid=target-lookup-id"
        data["actor"] = {"id": actor_id}
        data["targets"][0]["old_target"] = {"id": target_lookup_id}
        data["targets"][0]["new_target"]["id"] = target_lookup_id
        target_id_provided = "uid=target-id"
        data["targets"][1]["old_target"]["id"] = target_id_provided
        data["targets"][1]["new_target"]["id"] = target_id_provided

        opa_async_mock.return_value = [
            {"target_id": "", "result": True},
            {"target_id": target_lookup_id, "result": False},
            {"target_id": target_id_provided, "result": False},
        ]
        users = {
            target_lookup_id: MockUdmObject(
                dn=target_lookup_id,
                properties={"guardianRoles": ["ucsschool:users:student"]},
            ),
            actor_id: MockUdmObject(
                dn=actor_id, properties={"guardianRoles": ["ucsschool:users:teacher"]}
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("check_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()
        assert response.json() == {
            "actor_id": "actor-id",
            "permissions_check_results": [
                {"target_id": target_lookup_id, "actor_has_permissions": False},
                {"target_id": target_id_provided, "actor_has_permissions": False},
            ],
            "actor_has_all_general_permissions": True,
            "actor_has_all_targeted_permissions": False,
        }

    @pytest.mark.asyncio
    async def test_check_permissions_with_lookup_raises_404_if_object_not_found(
        self, client, udm_mock, opa_async_mock
    ):
        data = get_authz_permissions_check_request_dict(n_actor_roles=0, n_targets=1)
        actor_id = "actor-id"
        target_id = "uid=target-id"
        data["actor"] = {"id": actor_id}
        data["targets"][0]["old_target"] = {"id": target_id}
        data["targets"][0]["new_target"]["id"] = target_id
        opa_async_mock.return_value = [
            {"target_id": "", "result": True},
            {"target_id": target_id, "result": False},
        ]
        users = {
            actor_id: MockUdmObject(
                dn=actor_id, properties={"guardianRoles": ["ucsschool:users:teacher"]}
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("check_permissions_with_lookup"), json=data
        )
        assert response.status_code == 404, response.json()
        assert response.json() == {
            "detail": {
                "message": f"Could not find object of type 'USER' with identifier '{target_id}'."
            }
        }
        users = {
            target_id: MockUdmObject(
                dn=target_id, properties={"guardianRoles": ["ucsschool:users:student"]}
            ),
        }
        _udm_mock = udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("check_permissions_with_lookup"), json=data
        )
        assert response.status_code == 404, response.json()
        assert response.json() == {
            "detail": {
                "message": f"Could not find object of type 'USER' with identifier '{actor_id}'."
            }
        }

    @pytest.mark.asyncio
    async def test_permissions_check_with_lookup_udm_errors(
        self, client, opa_check_permissions_mock, udm_mock
    ):
        data = get_authz_permissions_check_request_dict()
        error_msg = "Test persistence error"
        _udm_mock = udm_mock(users={})
        with patch.object(
            MockUDMModule, "get", side_effect=PersistenceError(error_msg)
        ):
            response = client.post(
                client.app.url_path_for("check_permissions_with_lookup"), json=data
            )
        assert response.status_code == 500, response.json()
        assert response.json() == {"detail": {"message": error_msg}}

        error_msg = "Test general error"
        with patch.object(MockUDMModule, "get", side_effect=Exception(error_msg)):
            response = client.post(
                client.app.url_path_for("check_permissions_with_lookup"), json=data
            )
        assert response.status_code == 500, response.json()
        assert response.json() == {"detail": {"message": "Internal server error."}}


@pytest.mark.skipif(not opa_is_running(), reason="Needs a running OPA instance.")
@pytest.mark.in_container_test
class TestPermissionsCheck:
    @pytest.mark.asyncio
    async def test_permission_check_randomized_data(self, client):
        data = get_authz_permissions_check_request_dict(n_permissions=10, n_targets=10)
        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 200, response.json()
        expected_values = {
            element["target_id"]: element
            for element in [
                {
                    "actor_has_permissions": False,
                    "target_id": target["old_target"]["id"],
                }
                for target in data["targets"]
            ]
        }
        received_values = {
            element["target_id"]: element
            for element in response.json()["permissions_check_results"]
        }
        assert expected_values == received_values
        response_json = response.json()
        del response_json["permissions_check_results"]
        assert response_json == {
            "actor_has_all_general_permissions": False,
            "actor_has_all_targeted_permissions": False,
            "actor_id": data["actor"]["id"],
        }

    @pytest.mark.asyncio
    async def test_permission_check_basic(self, client):
        """
        - Actor has one role: ucsschool:users:teacher
        - According to the role-capability-mapping,
          the actor should always have the permission read_first_name
        """
        data = get_authz_permissions_check_request_dict(n_actor_roles=1, n_targets=1)
        data["actor"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "teacher"}
        ]

        data["contexts"] = []
        data["targeted_permissions_to_check"] = [
            {
                "app_name": "ucsschool",
                "namespace_name": "users",
                "name": "read_first_name",
            }
        ]
        data["general_permissions_to_check"] = []
        data["targets"][0]["old_target"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "teacher"}
        ]
        data["targets"][0]["new_target"] = data["targets"][0]["old_target"]
        data["namespaces"] = [{"app_name": "ucsschool", "name": "users"}]

        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 200, response.json()

        assert response.json() == {
            "actor_id": data["actor"]["id"],
            "permissions_check_results": [
                {
                    "target_id": data["targets"][0]["old_target"]["id"],
                    "actor_has_permissions": True,
                },
            ],
            "actor_has_all_targeted_permissions": True,
            "actor_has_all_general_permissions": False,
        }

    @pytest.mark.asyncio
    async def test_permission_check_general_permissions(self, client):
        data = get_authz_permissions_check_request_dict(n_actor_roles=1, n_targets=1)

        data["namespaces"] = [
            {"app_name": "ucsschool", "name": "users"},
            {"app_name": "oxmail", "name": "mail"},
        ]
        data["actor"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "teacher"}
        ]

        data["targeted_permissions_to_check"] = [
            {
                "app_name": "ucsschool",
                "namespace_name": "users",
                "name": "write_password",
            }
        ]
        data["general_permissions_to_check"] = [
            {
                "app_name": "oxmail",
                "namespace_name": "mail",
                "name": "export",
            }
        ]

        data["targets"][0]["old_target"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "student"}
        ]
        data["targets"][0]["old_target"]["attributes"]["school"] = "school1"
        data["targets"][0]["new_target"] = data["targets"][0]["old_target"]

        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 200, response.json()

        assert response.json() == {
            "actor_id": data["actor"]["id"],
            "permissions_check_results": [
                {
                    "target_id": data["targets"][0]["old_target"]["id"],
                    "actor_has_permissions": True,
                },
            ],
            "actor_has_all_targeted_permissions": True,
            "actor_has_all_general_permissions": True,
        }

    @pytest.mark.asyncio
    async def test_permission_check_conditions(self, client):
        data = get_authz_permissions_check_request_dict(n_actor_roles=1, n_targets=1)

        data["namespaces"] = [{"app_name": "ucsschool", "name": "users"}]
        data["actor"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "teacher"}
        ]

        data["targeted_permissions_to_check"] = []
        data["general_permissions_to_check"] = [
            {
                "app_name": "ucsschool",
                "namespace_name": "users",
                "name": "export",
            }
        ]
        data["targets"][0]["old_target"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "student"}
        ]
        data["targets"][0]["old_target"]["attributes"]["school"] = "school1"
        data["targets"][0]["new_target"] = data["targets"][0]["old_target"]

        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 200, response.json()

        assert response.json() == {
            "actor_id": data["actor"]["id"],
            "permissions_check_results": [],
            "actor_has_all_targeted_permissions": False,
            "actor_has_all_general_permissions": True,
        }

    @pytest.mark.asyncio
    async def test_check_permissions_with_lookup_randomized_data(
        self, client, udm_mock
    ):
        data = get_authz_permissions_check_request_dict(n_actor_roles=0, n_targets=1)
        actor_id = "actor-id"
        target_id = "uid=target-id"
        data["actor"] = {"id": actor_id}
        data["targets"][0]["old_target"] = {"id": target_id}
        data["targets"][0]["new_target"]["id"] = target_id
        data["contexts"] = []
        data["extra_request_data"] = {}
        data["targeted_permissions_to_check"] = [
            {
                "app_name": "ucsschool",
                "namespace_name": "users",
                "name": "read_first_name",
            }
        ]
        data["general_permissions_to_check"] = []
        data["namespaces"] = [{"app_name": "ucsschool", "name": "users"}]
        data["targets"][0]["new_target"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "teacher"}
        ]
        data["targets"][0]["new_target"]["attributes"] = {}
        users = {
            target_id: MockUdmObject(
                dn=target_id, properties={"guardianRoles": ["ucsschool:users:student"]}
            ),
            actor_id: MockUdmObject(
                dn=actor_id, properties={"guardianRoles": ["ucsschool:users:teacher"]}
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("check_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()
        expected_values = {
            element["target_id"]: element
            for element in [
                {
                    "actor_has_permissions": True,
                    "target_id": target["old_target"]["id"],
                }
                for target in data["targets"]
            ]
        }
        received_values = {
            element["target_id"]: element
            for element in response.json()["permissions_check_results"]
        }
        assert received_values == expected_values
        response_json = response.json()
        del response_json["permissions_check_results"]
        assert response_json == {
            "actor_id": actor_id,
            "actor_has_all_general_permissions": False,
            "actor_has_all_targeted_permissions": True,
        }

    @pytest.mark.asyncio
    async def test_check_permissions_with_lookup_basic(self, client, udm_mock):
        """
        - Actor has one role: ucsschool:users:teacher
        - According to the role-capability-mapping,
          the actor should always have the permission read_first_name

        -> actor and target are looked up
        """
        data = get_authz_permissions_check_request_dict(n_actor_roles=1, n_targets=1)
        actor_id = "actor-id"
        target_id = "uid=target-id"
        users = {
            target_id: MockUdmObject(
                dn=target_id, properties={"guardianRoles": ["ucsschool:users:student"]}
            ),
            actor_id: MockUdmObject(
                dn=actor_id, properties={"guardianRoles": ["ucsschool:users:teacher"]}
            ),
        }
        udm_mock(users=users)
        data["actor"] = {"id": actor_id}
        data["contexts"] = []
        data["targeted_permissions_to_check"] = [
            {
                "app_name": "ucsschool",
                "namespace_name": "users",
                "name": "read_first_name",
            }
        ]
        data["general_permissions_to_check"] = []
        data["targets"][0]["old_target"] = {"id": target_id}
        data["targets"][0]["new_target"]["id"] = target_id
        data["namespaces"] = [{"app_name": "ucsschool", "name": "users"}]

        response = client.post(
            client.app.url_path_for("check_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()

        assert response.json() == {
            "actor_id": actor_id,
            "permissions_check_results": [
                {
                    "target_id": target_id,
                    "actor_has_permissions": True,
                },
            ],
            "actor_has_all_targeted_permissions": True,
            "actor_has_all_general_permissions": False,
        }

    @pytest.mark.asyncio
    async def test_check_permissions_with_lookup_partial_basic(self, client, udm_mock):
        """
        Same as test_check_permissions_with_lookup_basic but
            one of the targets are looked up, one is provided.
        """
        data = get_authz_permissions_check_request_dict(n_actor_roles=1, n_targets=2)
        actor_id = "actor-id"
        lookup_target_id = "uid=target-lookup-id"
        users = {
            lookup_target_id: MockUdmObject(
                dn=lookup_target_id,
                properties={"guardianRoles": ["ucsschool:users:student"]},
            ),
            actor_id: MockUdmObject(
                dn=actor_id, properties={"guardianRoles": ["ucsschool:users:teacher"]}
            ),
        }
        udm_mock(users=users)
        data["actor"] = {"id": actor_id}
        data["contexts"] = []
        data["targeted_permissions_to_check"] = [
            {
                "app_name": "ucsschool",
                "namespace_name": "users",
                "name": "read_first_name",
            }
        ]
        data["general_permissions_to_check"] = []
        data["targets"][0]["old_target"] = {"id": lookup_target_id}
        data["targets"][0]["new_target"]["id"] = lookup_target_id
        target_id_provided = "uid=target-id"
        data["targets"][1]["old_target"]["id"] = target_id_provided
        data["targets"][1]["old_target"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "teacher"}
        ]
        data["targets"][1]["new_target"] = data["targets"][1]["old_target"]
        data["namespaces"] = [{"app_name": "ucsschool", "name": "users"}]
        response = client.post(
            client.app.url_path_for("check_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()
        assert response.json() == {
            "actor_id": actor_id,
            "permissions_check_results": [
                {
                    "target_id": target_id_provided,
                    "actor_has_permissions": True,
                },
                {
                    "target_id": lookup_target_id,
                    "actor_has_permissions": True,
                },
            ],
            "actor_has_all_targeted_permissions": True,
            "actor_has_all_general_permissions": False,
        }

    @pytest.mark.asyncio
    async def test_permission_check_general_permissions_with_lookup(
        self, client, udm_mock
    ):
        data = get_authz_permissions_check_request_dict(n_actor_roles=1, n_targets=1)
        data["namespaces"] = [{"app_name": "ucsschool", "name": "users"}]
        actor_id = "actor-id"
        target_id = "uid=target-id"
        data["actor"] = {"id": actor_id}
        data["targets"][0]["old_target"] = {"id": target_id}
        data["targeted_permissions_to_check"] = [
            {
                "app_name": "ucsschool",
                "namespace_name": "users",
                "name": "write_password",
            }
        ]
        data["general_permissions_to_check"] = [
            {
                "app_name": "ucsschool",
                "namespace_name": "users",
                "name": "export",
            }
        ]
        data["targets"][0]["new_target"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "teacher"}
        ]
        data["targets"][0]["new_target"]["attributes"] = {"school": "school1"}
        users = {
            target_id: MockUdmObject(
                dn=target_id,
                properties={
                    "guardianRoles": ["ucsschool:users:student"],
                    "school": "school1",
                },
            ),
            actor_id: MockUdmObject(
                dn=actor_id,
                properties={
                    "guardianRoles": ["ucsschool:users:teacher"],
                    "school": "school1",
                },
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("check_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()
        assert response.json() == {
            "actor_id": actor_id,
            "permissions_check_results": [
                {
                    "target_id": target_id,
                    "actor_has_permissions": True,
                },
            ],
            "actor_has_all_targeted_permissions": True,
            "actor_has_all_general_permissions": True,
        }

    @pytest.mark.asyncio
    async def test_permission_check_conditions_with_lookup(self, client, udm_mock):
        data = get_authz_permissions_check_request_dict(n_actor_roles=1, n_targets=1)
        data["namespaces"] = [{"app_name": "ucsschool", "name": "users"}]
        actor_id = "actor-id"
        target_id = "uid=target-id"
        data["actor"] = {"id": actor_id}
        data["targets"][0]["old_target"] = {"id": target_id}
        data["targeted_permissions_to_check"] = []
        data["general_permissions_to_check"] = [
            {
                "app_name": "ucsschool",
                "namespace_name": "users",
                "name": "export",
            }
        ]
        data["targets"][0]["new_target"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "teacher"}
        ]
        data["targets"][0]["new_target"]["attributes"] = {"school": "school1"}
        users = {
            target_id: MockUdmObject(
                dn=target_id,
                properties={
                    "guardianRoles": ["ucsschool:users:student"],
                    "school": "school1",
                },
            ),
            actor_id: MockUdmObject(
                dn=actor_id,
                properties={
                    "guardianRoles": ["ucsschool:users:teacher"],
                    "school": "school1",
                },
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("check_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()
        assert response.json() == {
            "actor_id": actor_id,
            "permissions_check_results": [],
            "actor_has_all_targeted_permissions": False,
            "actor_has_all_general_permissions": True,
        }
