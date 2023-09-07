# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from guardian_authorization_api.ports import (
    CheckPermissionsAPIPort,
    CheckPermissionsAPIRequestObject,
    CheckPermissionsAPIResponseObject,
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


async def check_permissions(
    permissions_check_request: CheckPermissionsAPIRequestObject,
    check_permissions_api_port: CheckPermissionsAPIPort,
    policy_port: PolicyPort,
) -> CheckPermissionsAPIResponseObject:
    try:
        check_permissions_query = await check_permissions_api_port.to_policy_query(
            permissions_check_request
        )
        check_permissions_result = await policy_port.check_permissions(
            check_permissions_query
        )
        return await check_permissions_api_port.to_api_response(
            check_permissions_query.actor.id, check_permissions_result
        )
    except Exception as exc:
        raise (await check_permissions_api_port.transform_exception(exc)) from exc
