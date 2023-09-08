from guardian_lib.ports import AuthenticationPort


class AlwaysAuthorizedAdapter(AuthenticationPort):
    """Simple adapter to allow all callers"""

    class Config:
        is_cached = True
        alias = "always_authorized"

    async def authorized(self):
        return True


class NeverAuthorizedAdapter(AuthenticationPort):
    """Never allow any caller"""

    class Config:
        is_cached = True
        alias = "never_authorized"

    async def authorized(self):
        return False
