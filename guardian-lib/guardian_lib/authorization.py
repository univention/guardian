import functools

from guardian_lib.ports import AuthenticationPort


class UnauthorizedError(Exception):
    pass


async def check_authorization(func):
    """Check if caller is authorized"""

    @functools.wraps(func)
    async def wrapper_authorized(*args, **kwargs):
        try:
            authentication_adapter: AuthenticationPort = kwargs.pop(
                "authentication_adapter"
            )
        except KeyError:
            raise UnauthorizedError
        if not await authentication_adapter.authorized():
            raise UnauthorizedError
        return func(*args, **kwargs)

    return wrapper_authorized
