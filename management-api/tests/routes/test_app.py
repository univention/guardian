# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from guardian_management_api.constants import COMPLETE_URL
from guardian_management_api.main import app
from guardian_management_api.models.app import App


class TestAppEndpoints:
    @pytest.fixture(autouse=True)
    def client(self):
        return TestClient(app)

    @patch(
        "guardian_management_api.adapters.app.AppStaticDataAdapter._data.apps", new=[]
    )
    def test_post_app_minimal(self, client, register_test_adapters):
        response = client.post(
            app.url_path_for("create_app"), json={"name": "test_app"}
        )
        assert response.status_code == 200
        assert response.json() == {
            "app": {
                "app_admin": {
                    "display_name": "test_app Admin",
                    "name": "test_app-admin",
                    "role": {
                        "app_name": "guardian",
                        "display_name": "test_app App Admin",
                        "name": "app-admin",
                        "namespace_name": "test_app",
                        "resource_url": f"{COMPLETE_URL}/roles/test_app/app-admin",
                    },
                },
                "display_name": None,
                "name": "test_app",
                "resource_url": f"{COMPLETE_URL}/apps/test_app",
            }
        }

    @patch(
        "guardian_management_api.adapters.app.AppStaticDataAdapter._data.apps", new=[]
    )
    def test_post_app_all(self, client, register_test_adapters):
        response = client.post(
            app.url_path_for("create_app"),
            json={"name": "test_app", "display_name": "test_app display_name"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "app": {
                "app_admin": {
                    "display_name": "test_app Admin",
                    "name": "test_app-admin",
                    "role": {
                        "app_name": "guardian",
                        "display_name": "test_app App Admin",
                        "name": "app-admin",
                        "namespace_name": "test_app",
                        "resource_url": f"{COMPLETE_URL}/roles/test_app/app-admin",
                    },
                },
                "display_name": "test_app display_name",
                "name": "test_app",
                "resource_url": f"{COMPLETE_URL}/apps/test_app",
            }
        }

    @patch(
        "guardian_management_api.adapters.app.AppStaticDataAdapter._data.apps",
        new=[App(name="test_app2")],
    )
    def test_get_app(self, client, register_test_adapters):
        name: str = "test_app2"
        response = client.get(app.url_path_for("get_app", name=name))
        assert response.status_code == 200
        assert response.json() == {
            "app": {
                "app_admin": {
                    "display_name": "test_app2 Admin",
                    "name": "test_app2-admin",
                    "role": {
                        "app_name": "guardian",
                        "display_name": "test_app2 App Admin",
                        "name": "app-admin",
                        "namespace_name": "test_app2",
                        "resource_url": f"{COMPLETE_URL}/roles/test_app2/app-admin",
                    },
                },
                "display_name": None,
                "name": "test_app2",
                "resource_url": f"{COMPLETE_URL}/apps/test_app2",
            }
        }

    @patch(
        "guardian_management_api.adapters.app.AppStaticDataAdapter._data.apps",
        new=[],
    )
    def test_get_app_404(self, client, register_test_adapters):
        name: str = "test_app3"
        response = client.get(app.url_path_for("get_app", name=name))
        assert response.status_code == 404
