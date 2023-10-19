from unittest.mock import patch

import pytest
from guardian_authorization_api.adapters.policies import OPAAdapter
from guardian_authorization_api.errors import PersistenceError
from pydantic import BaseModel, ValidationError

from ..conftest import get_authz_permissions_get_request_dict, opa_is_running
from ..mock_classes import MockUDMModule, MockUdmObject


class TestPermissionsGetUnittest:
    @pytest.mark.asyncio
    async def test_get_permissions_with_lookup(self, client, udm_mock, opa_async_mock):
        data = get_authz_permissions_get_request_dict(n_targets=1)
        actor_id = "actor-id"
        target_id = "uid=target-id"
        data["actor"] = {"id": actor_id}
        data["targets"][0]["old_target"] = {"id": target_id}
        data["targets"][0]["new_target"]["id"] = target_id
        opa_async_mock.return_value = [
            {"target_id": "", "result": True, "permissions": {}},
            {"target_id": target_id, "result": False, "permissions": {}},
        ]
        users = {
            target_id: MockUdmObject(
                dn=target_id, properties={"guardianRole": ["ucsschool:users:student"]}
            ),
            actor_id: MockUdmObject(
                dn=actor_id, properties={"guardianRole": ["ucsschool:users:teacher"]}
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("get_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()

        response_json = response.json()
        assert len(response_json["target_permissions"]) == len(data["targets"])
        assert {
            "permissions": [],
            "target_id": target_id,
        } in response_json["target_permissions"]
        assert response_json["general_permissions"] == []

    @pytest.mark.asyncio
    async def test_get_permissions_with_lookup_partial(
        self, client, udm_mock, opa_async_mock
    ):
        data = get_authz_permissions_get_request_dict(n_targets=2)
        actor_id = "actor-id"
        target_id_provided = "uid=target-id"
        data["actor"] = {"id": actor_id}
        data["targets"][0]["old_target"]["id"] = target_id_provided
        data["targets"][0]["new_target"]["id"] = target_id_provided
        target_lookup_id = "uid=target-lookup-id"
        data["targets"][1]["old_target"] = {"id": target_lookup_id}
        data["targets"][1]["new_target"]["id"] = target_lookup_id

        opa_async_mock.return_value = [
            {"target_id": "", "result": True, "permissions": {}},
            {"target_id": target_id_provided, "result": False, "permissions": {}},
            {"target_id": target_lookup_id, "result": False, "permissions": {}},
        ]
        users = {
            actor_id: MockUdmObject(
                dn=actor_id, properties={"guardianRole": ["ucsschool:users:teacher"]}
            ),
            target_lookup_id: MockUdmObject(
                dn=target_lookup_id,
                properties={"guardianRole": ["ucsschool:users:student"]},
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("get_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()

        response_json = response.json()
        assert len(response_json["target_permissions"]) == len(data["targets"])
        assert {
            "permissions": [],
            "target_id": target_id_provided,
        } in response_json["target_permissions"]
        assert response_json["general_permissions"] == []

    @pytest.mark.asyncio
    async def test_get_permissions_with_lookup_raises_404_if_object_not_found(
        self, client, udm_mock, opa_async_mock
    ):
        data = get_authz_permissions_get_request_dict(n_targets=1)
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
                dn=actor_id, properties={"guardianRole": ["ucsschool:users:teacher"]}
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("get_permissions_with_lookup"), json=data
        )
        assert response.status_code == 404, response.json()
        assert response.json() == {
            "detail": {
                "message": f"Could not find object of type 'USER' with identifier '{target_id}'."
            }
        }
        users = {
            target_id: MockUdmObject(
                dn=target_id, properties={"guardianRole": ["ucsschool:users:student"]}
            ),
        }
        _udm_mock = udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("get_permissions_with_lookup"), json=data
        )
        assert response.status_code == 404, response.json()
        assert response.json() == {
            "detail": {
                "message": f"Could not find object of type 'USER' with identifier '{actor_id}'."
            }
        }

    @pytest.mark.asyncio
    async def test_permissions_get_with_lookup_udm_errors(
        self, client, opa_check_permissions_mock, udm_mock
    ):
        data = get_authz_permissions_get_request_dict(n_targets=1)
        error_msg = "Test persistence error"
        _udm_mock = udm_mock(users={})
        with patch.object(
            MockUDMModule, "get", side_effect=PersistenceError(error_msg)
        ):
            response = client.post(
                client.app.url_path_for("get_permissions_with_lookup"), json=data
            )
        assert response.status_code == 500, response.json()
        assert response.json() == {"detail": {"message": error_msg}}

        error_msg = "Test general error"
        with patch.object(MockUDMModule, "get", side_effect=Exception(error_msg)):
            response = client.post(
                client.app.url_path_for("get_permissions_with_lookup"), json=data
            )
        assert response.status_code == 500, response.json()
        assert response.json() == {"detail": {"message": "Internal server error."}}

    @pytest.mark.asyncio
    async def test_permissions_get_opa_errors(self, client, opa_async_mock, udm_mock):
        opa_async_mock.return_value = 1
        actor_id = "actor-id"
        target_id = "uid=target-id"
        data = get_authz_permissions_get_request_dict(n_targets=1)
        data["actor"] = {"id": actor_id}
        data["targets"][0]["old_target"] = {"id": target_id}
        data["targets"][0]["new_target"]["id"] = target_id
        users = {
            target_id: MockUdmObject(
                dn=target_id, properties={"guardianRole": ["ucsschool:users:student"]}
            ),
            actor_id: MockUdmObject(
                dn=actor_id, properties={"guardianRole": ["ucsschool:users:teacher"]}
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("get_permissions_with_lookup"), json=data
        )
        assert response.status_code == 500, response.json()
        assert response.json() == {
            "detail": {"message": "Upstream returned faulty data for get_permissions."}
        }

        opa_async_mock.side_effect = Exception("Testexception")

        response = client.post(
            client.app.url_path_for("get_permissions_with_lookup"), json=data
        )
        assert response.status_code == 500, response.json()
        assert response.json() == {
            "detail": {"message": "Upstream error while getting permissions."}
        }

        data["targeted_permissions_to_check"] = []
        response = client.post(
            client.app.url_path_for("get_permissions_with_lookup"), json=data
        )
        assert response.status_code == 500, response.json()
        assert response.json() == {
            "detail": {"message": "Upstream error while getting permissions."}
        }

    @pytest.mark.asyncio
    async def test_get_permissions_validation_errors(self, client, udm_mock):
        data = get_authz_permissions_get_request_dict(n_targets=1)
        with patch.object(
            OPAAdapter, "get_permissions", side_effect=ValidationError([], BaseModel)
        ):
            response = client.post(
                client.app.url_path_for("get_permissions"), json=data
            )
        assert response.status_code == 422, response.json()
        # the number 0 is not relevant in this case, we just want to check
        # that the right status code and message are returned
        assert response.json() == {
            "detail": {"message": "0 validation errors for BaseModel\n"}
        }


@pytest.mark.skipif(not opa_is_running(), reason="Needs a running OPA instance.")
@pytest.mark.in_container_test
class TestGetPermissions:
    @pytest.mark.asyncio
    async def test_get_permissions_randomized_data(self, client):
        data = get_authz_permissions_get_request_dict(n_targets=10)

        response = client.post(client.app.url_path_for("get_permissions"), json=data)
        assert response.status_code == 200, response.json()

        response_json = response.json()

        assert len(response_json["target_permissions"]) == len(data["targets"])

        for target in data["targets"]:
            assert {
                "permissions": [],
                "target_id": target["old_target"]["id"],
            } in response_json["target_permissions"]

        assert response_json["general_permissions"] == []

    @pytest.mark.asyncio
    async def test_get_permissions_basic(self, client):
        """
        - Actor has one role: ucsschool:users:teacher
        - According to the role-capability-mapping,
          the actor should always have the checked permissions
        """
        data = get_authz_permissions_get_request_dict(n_actor_roles=1, n_targets=1)
        data["actor"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "teacher"}
        ]
        data["namespaces"] = [{"app_name": "ucsschool", "name": "users"}]
        response = client.post(client.app.url_path_for("get_permissions"), json=data)
        assert response.status_code == 200, response.json()

        response_json = response.json()
        assert response_json["actor_id"] == data["actor"]["id"]

        assert (
            response_json["target_permissions"][0]["target_id"]
            == data["targets"][0]["old_target"]["id"]
        )
        assert response_json["target_permissions"][0]["permissions"] == [
            {"app_name": "ucsschool", "name": "export", "namespace_name": "users"},
            {
                "app_name": "ucsschool",
                "name": "read_first_name",
                "namespace_name": "users",
            },
            {
                "app_name": "ucsschool",
                "name": "read_last_name",
                "namespace_name": "users",
            },
            {
                "app_name": "ucsschool",
                "name": "write_password",
                "namespace_name": "users",
            },
        ]

    @pytest.mark.asyncio
    async def test_get_permissions_randomized_data_with_lookup(self, client, udm_mock):
        data = get_authz_permissions_get_request_dict(n_targets=1)
        actor_id = "actor-id"
        target_id = "uid=target-id"
        data["actor"] = {"id": actor_id}
        data["namespaces"] = [{"app_name": "ucsschool", "name": "users"}]
        data["targets"][0]["old_target"] = {"id": target_id}
        data["targets"][0]["new_target"]["id"] = target_id
        users = {
            target_id: MockUdmObject(
                dn=target_id,
                properties={"guardianRole": ["ucsschool:users:other_user_type"]},
            ),
            actor_id: MockUdmObject(
                dn=actor_id,
                properties={"guardianRole": ["ucsschool:users:some_user_type"]},
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("get_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()
        response_json = response.json()
        assert len(response_json["target_permissions"]) == len(data["targets"])
        assert {
            "permissions": [],
            "target_id": target_id,
        } in response_json["target_permissions"]

        assert response_json["general_permissions"] == []

    @pytest.mark.asyncio
    async def test_get_permissions_basic_with_lookup(self, client, udm_mock):
        """
        - Actor has one role: ucsschool:users:teacher
        - According to the role-capability-mapping,
          the actor should always have the checked permissions
        """
        data = get_authz_permissions_get_request_dict(n_actor_roles=1, n_targets=1)
        data["namespaces"] = [{"app_name": "ucsschool", "name": "users"}]
        actor_id = "actor-id"
        target_id = "uid=target-id"
        data["actor"] = {"id": actor_id}
        data["targets"][0]["old_target"] = {"id": target_id}
        data["targets"][0]["new_target"]["id"] = target_id
        users = {
            target_id: MockUdmObject(
                dn=target_id, properties={"guardianRole": ["ucsschool:users:student"]}
            ),
            actor_id: MockUdmObject(
                dn=actor_id, properties={"guardianRole": ["ucsschool:users:teacher"]}
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("get_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()

        response_json = response.json()
        assert response_json["actor_id"] == data["actor"]["id"]
        assert (
            response_json["target_permissions"][0]["target_id"]
            == data["targets"][0]["old_target"]["id"]
        )
        assert response_json["target_permissions"][0]["permissions"] == [
            {"app_name": "ucsschool", "name": "export", "namespace_name": "users"},
            {
                "app_name": "ucsschool",
                "name": "read_first_name",
                "namespace_name": "users",
            },
            {
                "app_name": "ucsschool",
                "name": "read_last_name",
                "namespace_name": "users",
            },
            {
                "app_name": "ucsschool",
                "name": "write_password",
                "namespace_name": "users",
            },
        ]

    @pytest.mark.asyncio
    async def test_get_permissions_basic_with_lookup_partial(self, client, udm_mock):
        """
        Same as test_get_permissions_basic_with_lookup but
            one target is looked up, one is provided.
        """
        data = get_authz_permissions_get_request_dict(n_actor_roles=1, n_targets=2)
        actor_id = "actor-id"
        target_id_provided = "uid=provided-target-id"
        data["actor"] = {"id": actor_id}
        data["namespaces"] = [{"app_name": "ucsschool", "name": "users"}]
        data["targets"][0]["old_target"]["id"] = target_id_provided
        data["targets"][0]["new_target"]["id"] = target_id_provided
        target_lookup_id = "uid=target-lookup-id"
        data["targets"][1]["old_target"] = {"id": target_lookup_id}
        data["targets"][1]["new_target"]["id"] = target_lookup_id
        users = {
            target_lookup_id: MockUdmObject(
                dn=target_lookup_id,
                properties={"guardianRole": ["ucsschool:users:student"]},
            ),
            actor_id: MockUdmObject(
                dn=actor_id, properties={"guardianRole": ["ucsschool:users:teacher"]}
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("get_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()
        response_json = response.json()
        assert response_json["actor_id"] == data["actor"]["id"]
        assert (
            response_json["target_permissions"][0]["target_id"]
            == data["targets"][0]["old_target"]["id"]
        )
        for permission in response_json["target_permissions"]:
            assert permission["permissions"] == [
                {"app_name": "ucsschool", "name": "export", "namespace_name": "users"},
                {
                    "app_name": "ucsschool",
                    "name": "read_first_name",
                    "namespace_name": "users",
                },
                {
                    "app_name": "ucsschool",
                    "name": "read_last_name",
                    "namespace_name": "users",
                },
                {
                    "app_name": "ucsschool",
                    "name": "write_password",
                    "namespace_name": "users",
                },
            ]

    @pytest.mark.asyncio
    async def test_get_permissions_basic_with_lookup_context(self, client, udm_mock):
        """
        - Actor has one role: ucsschool:users:teacher
        - According to the role-capability-mapping,
          the actor should always have the checked permissions
        """
        data = get_authz_permissions_get_request_dict(n_actor_roles=1, n_targets=1)
        data["namespaces"] = [{"app_name": "ucsschool", "name": "users"}]
        actor_id = "actor-id"
        target_id = "uid=target-id"
        data["actor"] = {"id": actor_id}
        data["targets"][0]["old_target"] = {"id": target_id}
        data["targets"][0]["new_target"]["id"] = target_id
        users = {
            target_id: MockUdmObject(
                dn=target_id,
                properties={
                    "guardianRole": ["ucsschool:users:student&ucsschool:users:school1"]
                },
            ),
            actor_id: MockUdmObject(
                dn=actor_id,
                properties={
                    "guardianRole": ["ucsschool:users:teacher&ucsschool:users:school2"]
                },
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("get_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()

        response_json = response.json()
        assert response_json["actor_id"] == data["actor"]["id"]
        assert (
            response_json["target_permissions"][0]["target_id"]
            == data["targets"][0]["old_target"]["id"]
        )
        assert response_json["target_permissions"][0]["permissions"] == [
            {"app_name": "ucsschool", "name": "export", "namespace_name": "users"},
            {
                "app_name": "ucsschool",
                "name": "read_first_name",
                "namespace_name": "users",
            },
            {
                "app_name": "ucsschool",
                "name": "read_last_name",
                "namespace_name": "users",
            },
            {
                "app_name": "ucsschool",
                "name": "write_password",
                "namespace_name": "users",
            },
        ]

    @pytest.mark.parametrize(
        "target_roles,expected",
        [
            (
                ["ucsschool:users:student&ucsschool:users:school1"],
                [
                    {
                        "app_name": "contextApp",
                        "namespace_name": "test",
                        "name": "context_test_permission",
                    }
                ],
            ),
            (
                [
                    "ucsschool:users:student&ucsschool:users:school2",
                    "ucsschool:users:student&ucsschool:users:school3",
                ],
                [
                    {
                        "app_name": "contextApp",
                        "namespace_name": "test",
                        "name": "context_test_permission",
                    }
                ],
            ),
            (["ucsschool:users:student"], []),
            (["ucsschool:users:student&ucsschool:users:school3"], []),
        ],
    )
    @pytest.mark.asyncio
    async def test_get_permissions_context_compare(
        self, client, udm_mock, target_roles, expected
    ):
        """
        - Actor has one role: ucsschool:users:teacher
        - According to the role-capability-mapping,
          the actor should always have the checked permissions
        """
        data = get_authz_permissions_get_request_dict(n_actor_roles=1, n_targets=1)
        data["namespaces"] = [{"app_name": "contextApp", "name": "test"}]
        actor_id = "actor-id"
        target_id = "uid=target-id"
        data["actor"] = {"id": actor_id}
        data["targets"][0]["old_target"] = {"id": target_id}
        data["targets"][0]["new_target"]["id"] = target_id
        users = {
            target_id: MockUdmObject(
                dn=target_id,
                properties={"guardianRole": target_roles},
            ),
            actor_id: MockUdmObject(
                dn=actor_id,
                properties={
                    "guardianRole": [
                        "ucsschool:users:head_master&ucsschool:users:school1",
                        "ucsschool:users:head_master&ucsschool:users:school2",
                    ]
                },
            ),
        }
        udm_mock(users=users)
        response = client.post(
            client.app.url_path_for("get_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()

        response_json = response.json()
        assert response_json["actor_id"] == data["actor"]["id"]
        assert (
            response_json["target_permissions"][0]["target_id"]
            == data["targets"][0]["old_target"]["id"]
        )
        assert response_json["target_permissions"][0]["permissions"] == expected
