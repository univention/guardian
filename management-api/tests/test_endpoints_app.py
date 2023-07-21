import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from guardian_management_api.main import app
from guardian_management_api.models.app import App

API_PREFIX = os.environ.get("GUARDIAN__MANAGEMENT__API_PREFIX", "/guardian/management")


class TestAppEndpoints:
    @pytest.fixture(autouse=True)
    def client(self):
        return TestClient(app)

    @patch(
        "guardian_management_api.adapters.app.AppStaticDataAdapter._data.apps", new=[]
    )
    def test_post_app(self, client, register_test_adapters):
        response = client.post(f"{API_PREFIX}/apps/register", json={"name": "test_app"})
        assert response.status_code == 200
        assert response.json() == {
            "name": "test_app",
            "display_name": None,
            "resource_url": "",
            "app_admin": {
                "display_name": "admin",
                "name": "admin",
                "namespace": "default",
            },
        }

    @patch(
        "guardian_management_api.adapters.app.AppStaticDataAdapter._data.apps",
        new=[App(name="test_app")],
    )
    def test_get_app(self, client, register_test_adapters):
        name: str = "test_app"
        response = client.get(f"{API_PREFIX}/apps/{name}")
        assert response.status_code == 200
        assert response.json() == {
            "name": "test_app",
            "display_name": None,
            "app_admin": {
                "display_name": "admin",
                "name": "admin",
                "namespace": "default",
            },
            "resource_url": "",
        }
