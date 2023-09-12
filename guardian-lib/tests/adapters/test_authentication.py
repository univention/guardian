import pytest
from fastapi import HTTPException, status
from guardian_lib.adapter_registry import ADAPTER_REGISTRY
from guardian_lib.adapters.authentication import (
    FastAPIAlwaysAuthorizedAdapter,
    FastAPINeverAuthorizedAdapter,
)
from guardian_lib.ports import AuthenticationPort
from port_loader.errors import DuplicatePortError


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "adapter,allowed",
    [(FastAPINeverAuthorizedAdapter, False), (FastAPIAlwaysAuthorizedAdapter, True)],
)
async def test_AuthorizedAdapter(adapter, allowed):
    try:
        ADAPTER_REGISTRY.register_port(AuthenticationPort)
    except DuplicatePortError:
        pass
    ADAPTER_REGISTRY.register_adapter(AuthenticationPort, adapter_cls=adapter)
    ADAPTER_REGISTRY.set_adapter(AuthenticationPort, adapter)
    active_adapter = await ADAPTER_REGISTRY.request_adapter(AuthenticationPort, adapter)

    if not allowed:
        with pytest.raises(HTTPException) as exc:
            active_adapter()
            assert exc.status_code == status.HTTP_401_UNAUTHORIZED
    else:
        active_adapter()
