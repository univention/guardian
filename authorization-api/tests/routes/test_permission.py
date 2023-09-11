# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


import pytest
from fastapi.testclient import TestClient
from guardian_authorization_api.main import app


@pytest.mark.e2e
class TestPermissionEndpoints:
    @pytest.fixture(autouse=True)
    def client(self):
        return TestClient(app)

    def test_get_permissions_with_lookup(self, client, register_test_adapters):
        app_name = "ucsschool"
        namespace_name = "users"
        actor_id = "actor_id"
        target_id = "target_id"
        data = {
            "namespaces": [{"app_name": app_name, "name": namespace_name}],
            "actor": {
                "id": actor_id,
            },
            "targets": [
                {
                    "old_target": {
                        "id": target_id,
                    },
                    "new_target": {
                        "id": target_id,
                        "roles": [
                            {
                                "app_name": app_name,
                                "namespace_name": namespace_name,
                                "name": "string",
                            }
                        ],
                        "attributes": {},
                    },
                }
            ],
            "contexts": [
                {
                    "app_name": app_name,
                    "namespace_name": namespace_name,
                    "name": "string",
                    "display_name": "string",
                }
            ],
            "include_general_permissions": False,
            "extra_request_data": {},
        }
        response = client.post(
            app.url_path_for("get_permissions_with_lookup"), json=data
        )
        assert response.status_code == 200, response.json()
