# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from guardian_lib.authorization import check_authorization

from guardian_authorization_api.ports import (
    GetPermissionsAPIPort,
    GetPermissionsAPIRequestObject,
    GetPermissionsAPIResponseObject,
    PolicyPort,
)


@check_authorization
async def get_permissions(
    api_request: GetPermissionsAPIRequestObject,
    get_permission_api_port: GetPermissionsAPIPort,
    policy_port: PolicyPort,
) -> GetPermissionsAPIResponseObject:
    query = await get_permission_api_port.to_policy_query(api_request)
    policy_result = await policy_port.get_permissions(query)
    return await get_permission_api_port.to_api_response(policy_result)
