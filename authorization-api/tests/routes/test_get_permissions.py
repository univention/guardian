import pytest
from fastapi.testclient import TestClient
from guardian_authorization_api.main import app

from ..conftest import get_authz_permissions_get_request_dict, opa_is_running


@pytest.mark.skipif(not opa_is_running(), reason="Needs a running OPA instance.")
@pytest.mark.in_container_test
class TestGetPermissions:
    @pytest.fixture(autouse=True)
    def client(self):
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_get_permissions_randomized_data(
        self, client, register_test_adapters
    ):
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
    async def test_get_permissions_basic(self, client, register_test_adapters):
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
        response_json["actor_id"] == data["actor"]["id"]
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
