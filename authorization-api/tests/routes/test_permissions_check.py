import os
from unittest.mock import AsyncMock

import guardian_authorization_api.business_logic
import pytest
import requests
from fastapi.testclient import TestClient
from guardian_authorization_api.errors import ObjectNotFoundError, PersistenceError
from guardian_authorization_api.main import app

from .conftest import get_authz_permissions_check_request_dict


class TestPermissionsCheckUnittest:
    @pytest.fixture(autouse=True)
    def client(self):
        return TestClient(app)

    @pytest.fixture()
    def opa_check_permissions_mock(self):
        old_method = (
            guardian_authorization_api.adapters.policies.OPAAdapter.check_permissions
        )
        guardian_authorization_api.adapters.policies.OPAAdapter.check_permissions = (
            AsyncMock()
        )
        yield guardian_authorization_api.adapters.policies.OPAAdapter.check_permissions
        guardian_authorization_api.adapters.policies.OPAAdapter.check_permissions = (
            old_method
        )

    @pytest.mark.asyncio
    async def test_permissions_check_udm_errors(
        self, client, register_test_adapters, opa_check_permissions_mock
    ):
        # FIXME move to with-lookup endpoint test file when implemented
        error_msg = "Test object not found error."
        opa_check_permissions_mock.side_effect = ObjectNotFoundError(error_msg)
        data = {
            "actor": {
                "id": "1",
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
            "permissions_to_check": [
                {"app_name": "app1", "namespace_name": "ns1", "name": "ps2"}
            ],
            "extra_request_data": {},
        }
        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 404, response.json()
        assert response.json() == {"detail": {"message": error_msg}}

        error_msg = "Test persistence error"
        opa_check_permissions_mock.side_effect = PersistenceError(error_msg)

        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 500, response.json()
        assert response.json() == {"detail": {"message": error_msg}}

        error_msg = "Test general"
        opa_check_permissions_mock.side_effect = Exception(error_msg)

        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 500, response.json()
        assert response.json() == {"detail": {"message": "Internal server error."}}

    @pytest.mark.asyncio
    async def test_permissions_check_opa_errors(
        self, client, register_test_adapters, opa_async_mock
    ):
        opa_async_mock.return_value = 1
        data = {
            "actor": {
                "id": "1",
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
            "permissions_to_check": [
                {"app_name": "app1", "namespace_name": "ns1", "name": "ps2"}
            ],
            "extra_request_data": {},
        }
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

        data["permissions_to_check"] = []
        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 500, response.json()
        assert response.json() == {
            "detail": {"message": "Upstream error while checking general permissions."}
        }

    @pytest.mark.asyncio
    async def test_permissions_check_minimal(
        self, client, register_test_adapters, opa_async_mock
    ):
        data = {
            "actor": {
                "id": "1",
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
            "permissions_to_check": [
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
            "actor_id": "1",
            "permissions_check_results": [
                {"target_id": "id1", "actor_has_permissions": False},
                {"target_id": "id2", "actor_has_permissions": True},
            ],
            "actor_has_all_general_permissions": True,
            "actor_has_all_permissions": False,
        }

    @pytest.mark.asyncio
    async def test_permissions_check_full(
        self,
        client,
        register_test_adapters,
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
            "actor_has_all_permissions": False,
        }


def opa_is_not_running():
    if "OPA_ADAPTER__URL" not in os.environ:
        return True
    try:
        response = requests.get(os.environ["OPA_ADAPTER__URL"])
    except requests.exceptions.ConnectionError:
        return True
    return response.status_code != 200


@pytest.mark.skipif(opa_is_not_running(), reason="Needs a running OPA instance.")
@pytest.mark.e2e
class TestPermissionsCheck:
    @pytest.fixture(autouse=True)
    def client(self):
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_permission_check_randomized_data(
        self, client, register_test_adapters
    ):
        # get random request data
        data = get_authz_permissions_check_request_dict(n_permissions=10, n_targets=10)

        response = client.post(client.app.url_path_for("check_permissions"), json=data)
        assert response.status_code == 200, response.json()

        # convert list of results to dictionary with target_ids as keys
        # TODO maybe the API should return it like this in the first place
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
            "actor_has_all_permissions": False,
            "actor_id": data["actor"]["id"],
        }

    @pytest.mark.asyncio
    async def test_permission_check_basic(self, client, register_test_adapters):
        """
        Actor has one role and tries to
        """
        data = get_authz_permissions_check_request_dict(n_actor_roles=1, n_targets=1)
        data["actor"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "teacher"}
        ]

        data["contexts"] = []
        data["permissions_to_check"] = [
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
            "actor_has_all_permissions": True,
            "actor_has_all_general_permissions": False,
        }

    @pytest.mark.asyncio
    async def test_permission_check_general_permissions(
        self, client, register_test_adapters
    ):
        data = get_authz_permissions_check_request_dict(n_actor_roles=1, n_targets=1)

        data["namespaces"] = [
            {"app_name": "ucsschool", "name": "users"},
            {"app_name": "OX", "name": "mail"},
        ]
        data["actor"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "teacher"}
        ]

        data["permissions_to_check"] = [
            {
                "app_name": "ucsschool",
                "namespace_name": "users",
                "name": "write_password",
            }
        ]
        data["general_permissions_to_check"] = [
            {
                "app_name": "OX",
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
            "actor_has_all_permissions": True,
            "actor_has_all_general_permissions": True,
        }

    @pytest.mark.asyncio
    async def test_permission_check_conditions(self, client, register_test_adapters):
        data = get_authz_permissions_check_request_dict(n_actor_roles=1, n_targets=1)

        data["namespaces"] = [{"app_name": "ucsschool", "name": "users"}]
        data["actor"]["roles"] = [
            {"app_name": "ucsschool", "namespace_name": "users", "name": "teacher"}
        ]

        data["permissions_to_check"] = []
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
            "actor_has_all_permissions": False,
            "actor_has_all_general_permissions": True,
        }
