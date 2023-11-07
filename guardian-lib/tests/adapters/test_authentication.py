# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from unittest.mock import Mock

import pytest
import requests
from fastapi import HTTPException, status
from guardian_lib.adapters.authentication import (
    FastAPIAlwaysAuthorizedAdapter,
    FastAPINeverAuthorizedAdapter,
    FastAPIOAuth2,
)
from guardian_lib.ports import AuthenticationPort
from starlette.requests import Request

pytest_plugins = "guardian_pytest.authentication"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "adapter,allowed",
    [(FastAPINeverAuthorizedAdapter, False), (FastAPIAlwaysAuthorizedAdapter, True)],
)
async def test_simple_AuthenticationAdapter(register_test_adapters, adapter, allowed):
    auth_adapter = await register_test_adapters.request_adapter(
        AuthenticationPort, adapter
    )

    if not allowed:
        with pytest.raises(HTTPException) as exc:
            auth_adapter()
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED
    else:
        auth_adapter()


class TestAuthenticationOAuthAdapter:
    @pytest.mark.asyncio
    async def test_shutdown_on_config_error(self, monkeypatch):
        mock_get = Mock(side_effect=requests.exceptions.RequestException("test"))
        monkeypatch.setattr(requests, "get", mock_get)
        Settings = FastAPIOAuth2.get_settings_cls()
        settings = Settings(well_known_url="http://example.com")
        with pytest.raises(RuntimeError) as exc:
            await FastAPIOAuth2().configure(settings)
            assert exc.value.code == 1

    @pytest.mark.asyncio
    async def test_good_token(self, auth_adapter_oauth, good_token):
        request = Request(
            scope={
                "type": "http",
                "headers": [(b"authorization", f"Bearer {good_token}".encode("utf-8"))],
            }
        )
        assert request.headers.get("Authorization")
        await auth_adapter_oauth(request)

    @pytest.mark.asyncio
    async def test_missing_token(self, auth_adapter_oauth):
        request = Request(
            scope={"type": "http", "headers": [(b"authorization", b"Bearer")]}
        )
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth(request)
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_bad_idp(
        self,
        auth_adapter_oauth,
        bad_idp_token,
    ):
        request = Request(
            scope={
                "type": "http",
                "headers": [
                    (b"authorization", f"Bearer {bad_idp_token}".encode("utf-8"))
                ],
            }
        )
        assert request.headers.get("Authorization")
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth(request)
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_expired(
        self,
        auth_adapter_oauth,
        expired_token,
    ):
        request = Request(
            scope={
                "type": "http",
                "headers": [
                    (b"authorization", f"Bearer {expired_token}".encode("utf-8"))
                ],
            }
        )
        assert request.headers.get("Authorization")
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth(request)
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_bad_audience(
        self,
        auth_adapter_oauth,
        bad_audience_token,
    ):
        request = Request(
            scope={
                "type": "http",
                "headers": [
                    (b"authorization", f"Bearer {bad_audience_token}".encode("utf-8"))
                ],
            }
        )
        assert request.headers.get("Authorization")
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth(request)
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_bad_signature(
        self,
        auth_adapter_oauth,
        bad_signature_token,
    ):
        request = Request(
            scope={
                "type": "http",
                "headers": [
                    (b"authorization", f"Bearer {bad_signature_token}".encode("utf-8"))
                ],
            }
        )
        assert request.headers.get("Authorization")
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth(request)
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_wrong_key(
        self,
        auth_adapter_oauth,
        wrong_key_token,
    ):
        request = Request(
            scope={
                "type": "http",
                "headers": [
                    (b"authorization", f"Bearer {wrong_key_token}".encode("utf-8"))
                ],
            }
        )
        assert request.headers.get("Authorization")
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth(request)
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_actor_identifier(self, auth_adapter_oauth, good_token):
        request = Request(
            scope={
                "type": "http",
                "headers": [(b"authorization", f"Bearer {good_token}".encode("utf-8"))],
            }
        )
        assert request.headers.get("Authorization")
        result = await auth_adapter_oauth.get_actor_identifier(request)
        assert result == "dn"

    @pytest.mark.asyncio
    async def test_get_actor_identifier_bad_token(
        self,
        auth_adapter_oauth,
        expired_token,
    ):
        request = Request(
            scope={
                "type": "http",
                "headers": [
                    (b"authorization", f"Bearer {expired_token}".encode("utf-8"))
                ],
            }
        )
        assert request.headers.get("Authorization")
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth.get_actor_identifier(request)
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_actor_identifier_good_token_missing_dn(
        self, auth_adapter_oauth, good_token_wo_dn
    ):
        request = Request(
            scope={
                "type": "http",
                "headers": [
                    (b"authorization", f"Bearer {good_token_wo_dn}".encode("utf-8"))
                ],
            }
        )
        assert request.headers.get("Authorization")
        with pytest.raises(RuntimeError):
            await auth_adapter_oauth.get_actor_identifier(request)
