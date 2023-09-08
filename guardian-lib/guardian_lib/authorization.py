import functools

from guardian_lib.ports import AuthenticationPort


class UnauthorizedError(Exception):
    pass


def check_authorization(func):
    """Check if caller is authorized"""

    @functools.wraps(func)
    async def wrapper_authorized(*args, **kwargs):
        authentication_adapter: AuthenticationPort = kwargs.pop(
            "authentication_adapter"
        )
        if not await authentication_adapter.authorized():
            raise UnauthorizedError
        return await func(*args, **kwargs)

    return wrapper_authorized
