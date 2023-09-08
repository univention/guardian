import pytest
from guardian_lib.adapter_registry import ADAPTER_REGISTRY
from guardian_lib.adapters.authentication import (
    AlwaysAuthorizedAdapter,
    NeverAuthorizedAdapter,
)
from guardian_lib.authorization import UnauthorizedError, check_authorization
from guardian_lib.ports import AuthenticationPort
from port_loader.errors import DuplicatePortError


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "adapter,allowed",
    [(NeverAuthorizedAdapter, False), (AlwaysAuthorizedAdapter, True)],
)
async def test_AuthorizedAdapter(adapter, allowed):
    try:
        ADAPTER_REGISTRY.register_port(AuthenticationPort)
    except DuplicatePortError:
        pass
    ADAPTER_REGISTRY.register_adapter(AuthenticationPort, adapter_cls=adapter)
    ADAPTER_REGISTRY.set_adapter(AuthenticationPort, adapter)
    active_adapter = await ADAPTER_REGISTRY.request_adapter(AuthenticationPort, adapter)

    @check_authorization
    async def protected_function():
        return "I'm protected!"

    if not allowed:
        with pytest.raises(UnauthorizedError):
            await protected_function(authentication_adapter=active_adapter)
    else:
        assert "I'm protected!" == await protected_function(
            authentication_adapter=active_adapter
        )
