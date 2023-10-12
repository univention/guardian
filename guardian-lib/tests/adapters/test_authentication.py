# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from unittest.mock import Mock

import pytest
import requests
from fastapi import HTTPException, status
from guardian_lib.adapters.authentication import (
    ActorIdentifierOAuth2,
    FastAPIAlwaysAuthorizedAdapter,
    FastAPINeverAuthorizedAdapter,
    FastAPIOAuth2,
)
from guardian_lib.ports import ActorIdentifierPort, AuthenticationPort
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
        with pytest.raises(SystemExit) as exc:
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
        auth_adapter_oauth.fastapi_dependency(
            await auth_adapter_oauth.fastapi_oauth_dependency(request)
        )

    @pytest.mark.asyncio
    async def test_missing_token(self, auth_adapter_oauth):
        request = Request(
            scope={"type": "http", "headers": [(b"authorization", b"Bearer")]}
        )
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth.fastapi_dependency(
                await auth_adapter_oauth.fastapi_oauth_dependency(request)
            )
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
            await auth_adapter_oauth.fastapi_dependency(
                await auth_adapter_oauth.fastapi_oauth_dependency(request)
            )
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
            await auth_adapter_oauth.fastapi_dependency(
                await auth_adapter_oauth.fastapi_oauth_dependency(request)
            )
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
            await auth_adapter_oauth.fastapi_dependency(
                await auth_adapter_oauth.fastapi_oauth_dependency(request)
            )
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
            await auth_adapter_oauth.fastapi_dependency(
                await auth_adapter_oauth.fastapi_oauth_dependency(request)
            )
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
            await auth_adapter_oauth.fastapi_dependency(
                await auth_adapter_oauth.fastapi_oauth_dependency(request)
            )
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_ActorIdentifierOAuth2(
    auth_adapter_oauth, register_test_adapters, good_token
):
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"authorization", f"Bearer {good_token}".encode("utf-8"))],
        }
    )
    assert request.headers.get("Authorization")
    actor_adapter = await register_test_adapters.request_adapter(
        ActorIdentifierPort, ActorIdentifierOAuth2
    )
    assert "testi" == actor_adapter.fastapi_dependency(
        token=auth_adapter_oauth.fastapi_dependency(
            await auth_adapter_oauth.fastapi_oauth_dependency(request)
        )
    )
