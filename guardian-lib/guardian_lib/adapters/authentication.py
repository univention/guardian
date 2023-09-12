from fastapi import HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer

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


class FastAPIOAuth2(AuthenticationPort, OAuth2AuthorizationCodeBearer):
    class Config:
        is_cached = True
        alias = "fast_api_oauth2"

    def __init__(self):
        authorizationUrl = "https://ucs-sso-ng.ucs.test/realms/dev-guardian/protocol/openid-connect/auth"
        tokenUrl = "https://ucs-sso-ng.ucs.test/realms/dev-guardian/protocol/openid-connect/token"
        super.__init__(authorizationUrl=authorizationUrl, tokenUrl=tokenUrl)
