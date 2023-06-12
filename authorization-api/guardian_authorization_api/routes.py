from fastapi import APIRouter, Depends

from .adapters.base import port_dep
from .adapters.incoming import GetPermissionAPIPort
from .models.routes import AuthzPermissionsPostRequest, AuthzPermissionsPostResponse

router = APIRouter()


@router.post("/permissions")
async def get_permissions(
    permissions_fetch_request: AuthzPermissionsPostRequest,
    get_permission_api: GetPermissionAPIPort = Depends(port_dep(GetPermissionAPIPort)),
) -> AuthzPermissionsPostResponse:
    api_result = await get_permission_api.get_permissions(
        actor=permissions_fetch_request.actor.to_policy_object(),
        targets=[
            target.to_policies_target() for target in permissions_fetch_request.targets
        ]
        if permissions_fetch_request.targets
        else [],
        contexts=[],
        extra_request_data={},
        namespaces=[],
        include_general_permissions=permissions_fetch_request.include_general_permissions,
    )
    return AuthzPermissionsPostResponse.from_get_permissions_api_response(
        str(permissions_fetch_request.actor.id), api_result
    )
