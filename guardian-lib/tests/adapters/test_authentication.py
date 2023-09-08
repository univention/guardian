# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from datetime import datetime
from unittest.mock import Mock

import jwt
import pytest
import pytest_asyncio
import requests
from cryptography.hazmat.primitives import hashes
from fastapi import HTTPException, status
from guardian_lib.adapters.authentication import (
    FastAPIAlwaysAuthorizedAdapter,
    FastAPINeverAuthorizedAdapter,
    FastAPIOAuth2,
)
from guardian_lib.ports import AuthenticationPort
from jwt.algorithms import RSAAlgorithm
from starlette.requests import Request


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
    private_key_bad = """
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
"""

    private_key = """
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
"""

    public_key = """
-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAi/MWTgrdo14hX/N4lbWe
7Xabz5dvtAhZ6kW7ZgqoEgHDzSOSu8h100pMRWFvo6ZrLEQw/FUDhWGA3nnA6OHG
WplSVN/SWsEjxwmP2vYN8hPs8yUFjq256zPgo4fXcPIUsa1sAaobB1F0z9wrvgG7
g3KEQncYoeN0AVq82RaT4Fz0GFGHATY2KTaiweL8JGEphKb1qkBx9OjSbP8/99E7
P9K1SnCL8V1XUk+kQwraroydTw+//9JVGJWBvujhypO2hfqZvehs/74Ay9t4WvmV
7m2GVDcwMMGEGkuYqohzuV2B2CmLeeiqR1itLcN+l/Fl5btuagAqvFkebFSN+z2l
+sEluTQ0WCL3l7UTRIEYrQYNp9rw/VKM1uP51BfNDny236qWOshdbpSwXOqdqAV0
4ntZOPTE+JaL+cUYKpez8tsIhngx24ZnsTDE4scTNAbI057xmiqlEYUW1wZRK53b
/kVzoySiGLGzc4olD+iHC9HV2Crb1wg0Z9hYtxUSLdbZw/9eZBQSzzSBeTjTUTn+
hdZTUOV5xd5VgWw8DDnrHrNV5TvQd3M6RYXPp9Z405ZGDoplNJfKWRUJF3QRr9eW
WVPt58hcCRPmUNiPkmwlkjSX/MROq41+ZuAe5N09fOdS28MAOVaMXyIRCDLS6zP5
9zYKY3te+kujJ+1ciVt6I60CAwEAAQ==
-----END PUBLIC KEY-----
"""

    class MockWellKnownResponse:
        @staticmethod
        def json():
            return {
                "jwks_uri": "mock_response",
                "authorization_endpoint": "mock_response",
                "token_endpoint": "mock_response",
                "issuer": "guardian_idp",
            }

    @pytest.fixture
    def mock_well_known_response(self, monkeypatch):
        """Requests.get() mocked"""

        def mock_get(*args, **kwargs):
            return self.MockWellKnownResponse()

        monkeypatch.setattr(requests, "get", mock_get)

    @pytest.fixture
    def mock_get_jwk_set(self, monkeypatch):
        """jwt.jwks_client.PyJWKClient.get_jwk_set() mocked"""

        rsa = RSAAlgorithm(hashes.SHA256)
        key = rsa.prepare_key(self.public_key)
        jwk = rsa.to_jwk(key, as_dict=True)
        jwk["use"] = "sig"
        jwk["kid"] = "1234"
        data = {"keys": [jwk]}

        def mock_get_jwk_set(*args, **kwargs):
            return jwt.api_jwk.PyJWKSet.from_dict(data)

        monkeypatch.setattr(
            jwt.jwks_client.PyJWKClient, "get_jwk_set", mock_get_jwk_set
        )

    @pytest_asyncio.fixture
    async def auth_adapter_oauth(
        self, register_test_adapters, mock_well_known_response
    ):
        return await register_test_adapters.request_adapter(
            AuthenticationPort, FastAPIOAuth2
        )

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
    async def test_good_token(
        self, auth_adapter_oauth, mock_well_known_response, mock_get_jwk_set
    ):
        future_date = int(datetime.now().timestamp() + 300)
        encoded = jwt.encode(
            {
                "iss": "guardian_idp",
                "exp": f"{future_date}",
                "aud": "guardian",
                "sub": "testi",
                "client_id": "guardian",
                "iat": "0",
                "jti": "0",
            },
            self.private_key,
            algorithm="RS256",
            headers={"kid": "1234"},
        )
        request = Request(
            scope={
                "type": "http",
                "headers": [(b"authorization", f"Bearer {encoded}".encode("utf-8"))],
            }
        )
        assert request.headers.get("Authorization")
        await auth_adapter_oauth(request)

    @pytest.mark.asyncio
    async def test_missing_token(self, auth_adapter_oauth, mock_well_known_response):
        request = Request(
            scope={"type": "http", "headers": [(b"authorization", b"Bearer")]}
        )
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth(request)
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_bad_idp(
        self, auth_adapter_oauth, mock_well_known_response, mock_get_jwk_set
    ):
        future_date = int(datetime.now().timestamp() + 300)
        encoded = jwt.encode(
            {
                "iss": "bad",
                "exp": f"{future_date}",
                "aud": "guardian",
                "sub": "testi",
                "client_id": "guardian",
                "iat": "0",
                "jti": "0",
            },
            self.private_key,
            algorithm="RS256",
            headers={"kid": "1234"},
        )
        request = Request(
            scope={
                "type": "http",
                "headers": [(b"authorization", f"Bearer {encoded}".encode("utf-8"))],
            }
        )
        assert request.headers.get("Authorization")
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth(request)
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_expired(
        self, auth_adapter_oauth, mock_well_known_response, mock_get_jwk_set
    ):
        past_date = int(datetime.now().timestamp() - 300)
        encoded = jwt.encode(
            {
                "iss": "bad",
                "exp": f"{past_date}",
                "aud": "guardian",
                "sub": "testi",
                "client_id": "guardian",
                "iat": "0",
                "jti": "0",
            },
            self.private_key,
            algorithm="RS256",
            headers={"kid": "1234"},
        )
        request = Request(
            scope={
                "type": "http",
                "headers": [(b"authorization", f"Bearer {encoded}".encode("utf-8"))],
            }
        )
        assert request.headers.get("Authorization")
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth(request)
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_bad_audience(
        self, auth_adapter_oauth, mock_well_known_response, mock_get_jwk_set
    ):
        future_date = int(datetime.now().timestamp() + 300)
        encoded = jwt.encode(
            {
                "iss": "guardian_idp",
                "exp": f"{future_date}",
                "aud": "weather",
                "sub": "testi",
                "client_id": "guardian",
                "iat": "0",
                "jti": "0",
            },
            self.private_key,
            algorithm="RS256",
            headers={"kid": "1234"},
        )
        request = Request(
            scope={
                "type": "http",
                "headers": [(b"authorization", f"Bearer {encoded}".encode("utf-8"))],
            }
        )
        assert request.headers.get("Authorization")
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth(request)
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_bad_signature(
        self, auth_adapter_oauth, mock_well_known_response, mock_get_jwk_set
    ):
        future_date = int(datetime.now().timestamp() + 300)
        encoded = jwt.encode(
            {
                "iss": "guardian_idp",
                "exp": f"{future_date}",
                "aud": "guardian",
                "sub": "testi",
                "client_id": "guardian",
                "iat": "0",
                "jti": "0",
            },
            "secret",
            headers={"kid": "1234"},
        )
        request = Request(
            scope={
                "type": "http",
                "headers": [(b"authorization", f"Bearer {encoded}".encode("utf-8"))],
            }
        )
        assert request.headers.get("Authorization")
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth(request)
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_wrong_key(
        self, auth_adapter_oauth, mock_well_known_response, mock_get_jwk_set
    ):
        future_date = int(datetime.now().timestamp() + 300)
        encoded = jwt.encode(
            {
                "iss": "guardian_idp",
                "exp": f"{future_date}",
                "aud": "guardian",
                "sub": "testi",
                "client_id": "guardian",
                "iat": "0",
                "jti": "0",
            },
            self.private_key_bad,
            algorithm="RS256",
            headers={"kid": "1234"},
        )
        request = Request(
            scope={
                "type": "http",
                "headers": [(b"authorization", f"Bearer {encoded}".encode("utf-8"))],
            }
        )
        assert request.headers.get("Authorization")
        with pytest.raises(HTTPException) as exc:
            await auth_adapter_oauth(request)
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED
