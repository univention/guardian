# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

import sys
from typing import Annotated, Type

import jwt
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from port_loader import AsyncConfiguredAdapterMixin

from guardian_lib.adapter_registry import port_dep
from guardian_lib.models.authentication import FastAPIOAuth2AdapterSettings
from guardian_lib.ports import ActorIdentifierPort, AuthenticationPort


class FastAPIAlwaysAuthorizedAdapter(AuthenticationPort):
    """Simple adapter to allow all callers"""

    class Config:
        is_cached = True
        alias = "fast_api_always_authorized"

    @property
    def fastapi_dependency(self) -> None:
        def dependency_function():
            return dict()

        return dependency_function


class FastAPINeverAuthorizedAdapter(AuthenticationPort):
    """Never allow any caller"""

    class Config:
        is_cached = True
        alias = "fast_api_never_authorized"

    @property
    def fastapi_dependency(self):
        def dependency_function():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authorized",
            )

        return dependency_function


async def _get_fastapi_oauth_dependency():
    return await port_dep(AuthenticationPort, FastAPIOAuth2).fastapi_dependency


class FastAPIOAuth2(AuthenticationPort, AsyncConfiguredAdapterMixin):
    """
    Check an ouath token against the settings loaded from a ".well-known" oauth endpoint.
    OAuth2AuthorizationCodeBearer configures the openapi.json to include the login settings.
    If the openapi.json is configured, it's possible to login on the swagger ui.
    """

    class Config:
        is_cached = True
        alias = "fastapi_oauth"

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
        self.fastapi_oauth_dependency = OAuth2AuthorizationCodeBearer(
            tokenUrl=tokenUrl, authorizationUrl=authorizationUrl
        )

    @classmethod
    def get_settings_cls(cls) -> Type[FastAPIOAuth2AdapterSettings]:
        return FastAPIOAuth2AdapterSettings

    @property
    def fastapi_dependency(self):
        def dependency_function(
            token_encoded: Annotated[str, Depends(self.fastapi_oauth_dependency)]
        ) -> dict:
            return self.parse_token(token_encoded)

        return dependency_function

    def parse_token(self, token_encoded):
        try:
            token = jwt.decode(
                token_encoded,
                self.jwks_client.get_signing_key_from_jwt(token_encoded).key,
                algorithms=["RS256"],
                audience="guardian",
                issuer=self.oauth_settings["issuer"],
                options={
                    "require": ["exp", "iss", "aud", "sub", "client_id", "iat", "jti"]
                },
            )
        except jwt.exceptions.InvalidTokenError as exc:
            self.logger.warning(f'Invalid Token: "{exc}"', token_encoded=token_encoded)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authorized",
            )
        return token


class ActorIdentifierOAuth2(ActorIdentifierPort, AsyncConfiguredAdapterMixin):
    class Config:
        is_cached = True
        alias = "fast_api_actor_oauth"

    async def configure(self) -> None:
        self.oauth_dependency = await port_dep(AuthenticationPort, FastAPIOAuth2)

    @property
    def fastapi_dependency(self):
        def dependency_function(token: Annotated[dict, Depends(self.oauth_dependency)]):
            return token["sub"]

        return dependency_function


class ActorIdentifierStatic(ActorIdentifierPort):
    class Config:
        is_cached = True
        alias = "fast_api_actor_static"

    @property
    def fastapi_dependency(self):
        def dependency_function():
            return "uid=dev"

        return dependency_function
