# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from importlib import reload
from unittest.mock import patch

from fastapi.testclient import TestClient
from guardian_management_api import main
from guardian_management_api.constants import API_PREFIX
from port_loader import AsyncAdapterRegistry


class TestSetup:
    @patch(
        "guardian_management_api.main.ADAPTER_REGISTRY",
        new=AsyncAdapterRegistry(),
    )
    def test_lifespan(self, patch_env):
        # monkeypatch.setenv(
        #    "GUARDIAN__MANAGEMENT__ADAPTER__APP_PERSISTENCE_PORT", "in_memory"
        # )
        # monkeypatch.setenv("GUARDIAN__MANAGEMENT__ADAPTER__SETTINGS_PORT", "env")

        with TestClient(main.app) as client:
            response = client.get(f"{API_PREFIX}/docs")
            assert response.status_code == 200

    @patch(
        "guardian_management_api.main.ADAPTER_REGISTRY",
        new=AsyncAdapterRegistry(),
    )
    def test_cors_middleware_no_setting(self, patch_env):
        with patch("guardian_management_api.constants.CORS_ALLOWED_ORIGINS", None):
            reload(main)
            cors_middleware = list(
                filter(
                    lambda mw: mw.cls.__name__ == "CORSMiddleware",
                    main.app.user_middleware,
                )
            )
            assert len(cors_middleware) == 0

    @patch(
        "guardian_management_api.main.ADAPTER_REGISTRY",
        new=AsyncAdapterRegistry(),
    )
    def test_cors_middleware_all_hosts(self, patch_env):
        with patch("guardian_management_api.constants.CORS_ALLOWED_ORIGINS", "*"):
            reload(main)
            cors_middleware = list(
                filter(
                    lambda mw: mw.cls.__name__ == "CORSMiddleware",
                    main.app.user_middleware,
                )
            )
            assert len(cors_middleware) == 1
            assert cors_middleware[0].options["allow_origins"] == ["*"]

    @patch(
        "guardian_management_api.main.ADAPTER_REGISTRY",
        new=AsyncAdapterRegistry(),
    )
    def test_cors_middleware_multiple_hosts(self, patch_env):
        with patch(
            "guardian_management_api.constants.CORS_ALLOWED_ORIGINS",
            "http://localhost,http://univention.de",
        ):
            reload(main)
            cors_middleware = list(
                filter(
                    lambda mw: mw.cls.__name__ == "CORSMiddleware",
                    main.app.user_middleware,
                )
            )
            assert len(cors_middleware) == 1
            assert cors_middleware[0].options["allow_origins"] == [
                "http://localhost",
                "http://univention.de",
            ]
