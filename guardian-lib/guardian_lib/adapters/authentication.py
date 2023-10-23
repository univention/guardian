# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import sys
from typing import Any, Type

import jwt
import requests
from fastapi import HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from port_loader import AsyncConfiguredAdapterMixin
from starlette.requests import Request

from guardian_lib.models.authentication import FastAPIOAuth2AdapterSettings
from guardian_lib.ports import AuthenticationPort


class FastAPIAlwaysAuthorizedAdapter(AuthenticationPort[Request]):
    """Simple adapter to allow all callers"""

    class Config:
        is_cached = True
        alias = "fast_api_always_authorized"

    def __call__(self) -> None:
        return

    async def get_actor_identifier(self, request: Request) -> str:
        # just for testing, not used yet (so not covered)
        return "dev"  # pragma: no cover


class FastAPINeverAuthorizedAdapter(AuthenticationPort[Request]):
    """Never allow any caller"""

    class Config:
        is_cached = True
        alias = "fast_api_never_authorized"

    def __call__(self) -> None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
        )

    async def get_actor_identifier(self, request: Request) -> str:
        raise RuntimeError(
            "Shouldn't happen, this adapter never authenticates."
        )  # pragma: no cover


class FastAPIOAuth2(
    OAuth2AuthorizationCodeBearer,
    AuthenticationPort[Request],
    AsyncConfiguredAdapterMixin,
):
    """
    Check an ouath token against the settings loaded from a ".well-known" oauth endpoint.
    OAuth2AuthorizationCodeBearer configures the openapi.json to include the login settings.
    If the openapi.json is configured, it's possible to login on the swagger ui.
    """

    class Config:
        is_cached = True
        alias = "fast_api_oauth"

    def __init__(self):
        pass

    async def configure(self, settings: FastAPIOAuth2AdapterSettings) -> None:
        timeout = 10
        try:
            self.oauth_settings = requests.get(
                settings.well_known_url,
                timeout=timeout,
            ).json()
        except requests.exceptions.RequestException as exc:
            self.logger.critical(f'SHUTDOWN could not load oauth settings: "{exc}"')
            sys.exit(1)
        self.logger.debug("Loaded oauth settings", oauth_settings=self.oauth_settings)
        self.jwks_client = jwt.PyJWKClient(
            self.oauth_settings["jwks_uri"], timeout=timeout
        )
        authorizationUrl = self.oauth_settings["authorization_endpoint"]
        tokenUrl = self.oauth_settings["token_endpoint"]
        super().__init__(
            authorizationUrl=authorizationUrl,
            tokenUrl=tokenUrl,
            scopes={"openid": "scope for openid"},
        )

    @classmethod
    def get_settings_cls(cls) -> Type[FastAPIOAuth2AdapterSettings]:
        return FastAPIOAuth2AdapterSettings

    async def _get_decoded_token(self, request: Request) -> dict[str, Any]:
        token = await super().__call__(request)
        try:
            decoded_token = jwt.decode(
                token,
                self.jwks_client.get_signing_key_from_jwt(token).key,
                algorithms=["RS256"],
                audience="guardian",
                issuer=self.oauth_settings["issuer"],
                options={"require": ["exp", "iss", "aud", "sub", "iat", "jti"]},
            )
        except jwt.exceptions.InvalidTokenError as exc:
            self.logger.warning(f'Invalid Token: "{exc}"', token=token)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authorized",
            )

        return decoded_token

    async def __call__(self, request: Request) -> None:
        await self._get_decoded_token(request)

    async def get_actor_identifier(self, request: Request) -> str:
        decoded_token = await self._get_decoded_token(request)
        return decoded_token["sub"]
