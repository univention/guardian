# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from loguru import logger

from guardian_authorization_api.ports import (
    CheckPermissionsAPIPort,
    CheckPermissionsAPIRequestObject,
    CheckPermissionsAPIResponseObject,
    CheckPermissionsWithLookupAPIRequestObject,
    GetPermissionsAPIPort,
    GetPermissionsAPIRequestObject,
    GetPermissionsAPIResponseObject,
    GetPermissionsWithLookupAPIRequestObject,
    PersistencePort,
    PolicyPort,
)


async def get_permissions(
    api_request: GetPermissionsAPIRequestObject,
    get_permission_api_port: GetPermissionsAPIPort,
    policy_port: PolicyPort,
) -> GetPermissionsAPIResponseObject:
    try:
        query = await get_permission_api_port.to_policy_query(api_request)
        logger.debug("test", query=query)
        logger.debug(
            "Received request to retrieve permissions.",
            actor_id=query.actor.id,
            namespaces=query.namespaces,
        )
        policy_result = await policy_port.get_permissions(query)
        return await get_permission_api_port.to_api_response(policy_result)
    except Exception as exc:
        logger.error("Error while retriving permissions.")
        raise (await get_permission_api_port.transform_exception(exc)) from exc


async def check_permissions(
    permissions_check_request: CheckPermissionsAPIRequestObject,
    check_permissions_api_port: CheckPermissionsAPIPort,
    policy_port: PolicyPort,
) -> CheckPermissionsAPIResponseObject:
    try:
        check_permissions_query = await check_permissions_api_port.to_policy_query(
            permissions_check_request
        )
        logger.debug(
            "Received request to check permissions.",
            actor_id=check_permissions_query.actor.id,
            namespaces=check_permissions_query.namespaces,
        )
        check_permissions_result = await policy_port.check_permissions(
            check_permissions_query
        )
        return await check_permissions_api_port.to_api_response(
            check_permissions_query.actor.id, check_permissions_result
        )
    except Exception as exc:
        logger.error("Error while checking permissions.")
        raise (await check_permissions_api_port.transform_exception(exc)) from exc


async def check_permissions_with_lookup(
    api_request: CheckPermissionsWithLookupAPIRequestObject,
    check_permissions_api_port: CheckPermissionsAPIPort,
    policy_port: PolicyPort,
    persistence_port: PersistencePort,
):
    try:
        actor_id, old_target_ids = check_permissions_api_port.get_actor_and_target_ids(
            api_request=api_request
        )
        actor, old_targets = await persistence_port.lookup_actor_and_old_targets(
            actor_id=actor_id, old_target_ids=old_target_ids
        )
        check_permissions_query = (
            await check_permissions_api_port.to_policy_lookup_query(
                api_request=api_request, actor=actor, old_looked_up_targets=old_targets
            )
        )
        logger.debug(
            "Received request to check permissions with lookup.",
            actor_id=check_permissions_query.actor.id,
            namespaces=check_permissions_query.namespaces,
        )
        check_permissions_result = await policy_port.check_permissions(
            check_permissions_query
        )
        return await check_permissions_api_port.to_api_response(
            check_permissions_query.actor.id, check_permissions_result
        )
    except Exception as exc:
        logger.error("Error while checking permissions with lookup.")
        raise (await check_permissions_api_port.transform_exception(exc)) from exc


async def get_permissions_with_lookup(
    api_request: GetPermissionsWithLookupAPIRequestObject,
    get_permission_api: GetPermissionsAPIPort,
    policy_port: PolicyPort,
    persistence_port: PersistencePort,
):
    try:
        actor_id, old_target_ids = get_permission_api.get_actor_and_target_ids(
            api_request=api_request
        )
        actor, old_targets = await persistence_port.lookup_actor_and_old_targets(
            actor_id=actor_id, old_target_ids=old_target_ids
        )
        query = await get_permission_api.to_policy_lookup_query(
            api_request=api_request, actor=actor, old_looked_up_targets=old_targets
        )
        logger.debug(
            "Received request to retrieve permissions with lookup.",
            actor_id=query.actor.id,
            namespaces=query.namespaces,
        )
        policy_result = await policy_port.get_permissions(query)
        return await get_permission_api.to_api_response(policy_result)
    except Exception as exc:
        logger.error("Error while retrieving permissions with lookup.")
        raise (await get_permission_api.transform_exception(exc)) from exc
