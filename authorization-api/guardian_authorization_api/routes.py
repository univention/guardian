from fastapi import APIRouter, Depends

from . import business_logic
from .adapter_registry import port_dep
from .adapters.api import FastAPIGetPermissionsAPIAdapter, GetPermissionsAPIPort
from .models.routes import AuthzPermissionsPostRequest, AuthzPermissionsPostResponse
from .ports import PolicyPort

router = APIRouter()


@router.post("/permissions")
async def get_permissions(
    permissions_fetch_request: AuthzPermissionsPostRequest,
    get_permission_api: FastAPIGetPermissionsAPIAdapter = Depends(
        port_dep(GetPermissionsAPIPort, FastAPIGetPermissionsAPIAdapter)
    ),
    policy_port: PolicyPort = Depends(port_dep(PolicyPort)),
) -> AuthzPermissionsPostResponse:
    return await business_logic.get_permissions(
        permissions_fetch_request, get_permission_api, policy_port
    )
