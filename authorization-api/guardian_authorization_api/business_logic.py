# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from guardian_authorization_api.ports import (
    GetPermissionsAPIPort,
    GetPermissionsAPIRequestObject,
    GetPermissionsAPIResponseObject,
    PolicyPort, PersistencePort,
)
from guardian_authorization_api.models.persistence import ObjectType


async def get_permissions(
    api_request: GetPermissionsAPIRequestObject,
    get_permission_api_port: GetPermissionsAPIPort,
    policy_port: PolicyPort,
) -> GetPermissionsAPIResponseObject:
    query = await get_permission_api_port.to_policy_query(api_request)
    policy_result = await policy_port.get_permissions(query)
    return await get_permission_api_port.to_api_response(policy_result)


async def get_permissions_with_lookup(
    api_request: GetPermissionsAPIRequestObject,
    get_permission_api_port: GetPermissionsAPIPort,
    policy_port: PolicyPort,
    persistence_port: PersistencePort,
) -> GetPermissionsAPIResponseObject:
    try:
        actor = await persistence_port.get_object(identifier=api_request.actor.id, object_type=ObjectType.USER)
        # what if the object is something other than a user?
        # is this parsed from the roles?
        # old target / new target?
        targets = []
        for t in api_request.targets:
            targets.append(
                await persistence_port.get_object(identifier=t.old_target.id, object_type=ObjectType.USER)
            )
            targets.append(
                await persistence_port.get_object(identifier=t.new_target.id, object_type=ObjectType.USER)
            )
        query = await get_permission_api_port.to_policy_query_with_lookup(api_request, actor, targets)
        policy_result = await policy_port.get_permissions(query)
    except Exception as exc:
        raise exc
        # raise (
        #     await policy_port.transform_exception(exc)
        # ) from exc
    return await get_permission_api_port.to_api_response(policy_result)
