from unittest.mock import patch

from fastapi.testclient import TestClient
from guardian_management_api.constants import API_PREFIX
from guardian_management_api.main import app
from port_loader import AsyncAdapterRegistry


class TestSetup:
    @patch(
        "guardian_management_api.main.ADAPTER_REGISTRY",
        new=AsyncAdapterRegistry(),
    )
    def test_lifespan(self, monkeypatch):
        monkeypatch.setenv(
            "GUARDIAN__MANAGEMENT__ADAPTER__APP_PERSISTENCE_PORT", "in_memory"
        )
        monkeypatch.setenv("GUARDIAN__MANAGEMENT__ADAPTER__SETTINGS_PORT", "env")

        with TestClient(app) as client:
            response = client.get(f"{API_PREFIX}/docs")
            assert response.status_code == 200
