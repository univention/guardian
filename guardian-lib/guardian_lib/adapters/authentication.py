import ssl
from typing import Type

import jwt
import requests
from fastapi import HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from port_loader import AsyncConfiguredAdapterMixin
from starlette.requests import Request

from guardian_lib.models.authentication import FastAPIOAuth2AdapterSettings
from guardian_lib.ports import AuthenticationPort


class FastAPIAlwaysAuthorizedAdapter(AuthenticationPort):
    """Simple adapter to allow all callers"""

    class Config:
        is_cached = True
        alias = "fast_api_always_authorized"

    def __call__(self):
        return


class FastAPINeverAuthorizedAdapter(AuthenticationPort):
    """Never allow any caller"""

    class Config:
        is_cached = True
        alias = "fast_api_never_authorized"

    def __call__(self):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
        )


class FastAPIOAuth2(
    OAuth2AuthorizationCodeBearer, AuthenticationPort, AsyncConfiguredAdapterMixin
):
    class Config:
        is_cached = True
        alias = "fast_api_oauth"

    def __init__(self):
        pass

    async def configure(self, settings: FastAPIOAuth2AdapterSettings):
        timeout = 10
        self.oauth_settings = requests.get(
            settings.well_known_url,
            verify=settings.well_known_url_secure,
            timeout=timeout,
        ).json()
        if settings.well_known_url_secure:
            ctx = None
        else:
            ctx = self.__get_insecure_ssl_context()
        self.jwks_client = jwt.PyJWKClient(
            self.oauth_settings["jwks_uri"], ssl_context=ctx, timeout=timeout
        )
        authorizationUrl = self.oauth_settings["authorization_endpoint"]
        tokenUrl = self.oauth_settings["token_endpoint"]
        super().__init__(authorizationUrl=authorizationUrl, tokenUrl=tokenUrl)

    def __get_insecure_ssl_context(self) -> ssl.SSLContext:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    @classmethod
    def get_settings_cls(cls) -> Type[FastAPIOAuth2AdapterSettings]:
        return FastAPIOAuth2AdapterSettings

    async def __call__(self, request: Request):
        token = await super().__call__(request)
        try:
            jwt.decode(
                token,
                self.jwks_client.get_signing_key_from_jwt(token).key,
                algorithms=["RS256"],
                audience="guardian",
                issuer=self.oauth_settings["issuer"],
                options={
                    "require": ["exp", "iss", "aud", "sub", "client_id", "iat", "jti"]
                },
            )
        except jwt.exceptions.DecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not Authorized",
            )
