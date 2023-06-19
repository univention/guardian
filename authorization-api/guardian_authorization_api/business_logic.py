from guardian_authorization_api.ports import (
    GetPermissionsAPIPort,
    GetPermissionsAPIRequestObject,
    GetPermissionsAPIResponseObject,
    PolicyPort,
)


async def get_permissions(
    api_request: GetPermissionsAPIRequestObject,
    get_permission_api_port: GetPermissionsAPIPort,
    policy_port: PolicyPort,
) -> GetPermissionsAPIResponseObject:
    query = await get_permission_api_port.to_policy_query(api_request)
    policy_result = await policy_port.get_permissions(query)
    return await get_permission_api_port.to_api_response(policy_result)
