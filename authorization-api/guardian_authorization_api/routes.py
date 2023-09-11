# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from fastapi import APIRouter, Depends
from guardian_lib.adapter_registry import port_dep
from guardian_lib.ports import AuthenticationPort

from . import business_logic
from .adapters.api import FastAPIGetPermissionsAPIAdapter, GetPermissionsAPIPort
from .models.routes import (
    AuthzCustomEndpointPostRequest,
    AuthzCustomEndpointPostResponse,
    AuthzPermissionsCheckLookupPostRequest,
    AuthzPermissionsCheckPostRequest,
    AuthzPermissionsCheckPostResponse,
    AuthzPermissionsLookupPostRequest,
    AuthzPermissionsPostRequest,
    AuthzPermissionsPostResponse,
)
from .ports import PolicyPort

router = APIRouter()


@router.post("/permissions")
async def get_permissions(
    permissions_fetch_request: AuthzPermissionsPostRequest,
    get_permission_api: FastAPIGetPermissionsAPIAdapter = Depends(
        port_dep(GetPermissionsAPIPort, FastAPIGetPermissionsAPIAdapter)
    ),
    policy_port: PolicyPort = Depends(port_dep(PolicyPort)),
    authentication_adapter: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
) -> AuthzPermissionsPostResponse:
    """
    Retrieve a list of permissions for an actor, with optional targets.
    Actor and target objects must be supplied in their entirety.
    """
    return await business_logic.get_permissions(
        permissions_fetch_request,
        get_permission_api,
        policy_port,
        authentication_adapter=authentication_adapter,
    )


@router.post("/permissions/with-lookup")
async def get_permissions_with_lookup(  # pragma: no-cover
    permissions_with_lookup_request: AuthzPermissionsLookupPostRequest,
) -> AuthzPermissionsPostResponse:
    """
    Retrieve a list of permissions for an actor, with optional targets.
    Actor and target objects can be looked up by Guardian using an identifier.
    """
    # Example only; not implemented
    # Remove the pragma: no-cover when this is implemented
    return AuthzPermissionsPostResponse(
        actor_id=permissions_with_lookup_request.actor.id,
        general_permissions=[],
        target_permissions=[],
    )


@router.post("/permissions/check")
async def check_permissions(  # pragma: no-cover
    permissions_check_request: AuthzPermissionsCheckPostRequest,
) -> AuthzPermissionsCheckPostResponse:
    """
    Retrieve a yes/no answer to whether an actor has all specified permissions.
    May optionally include targets.
    Actor and target objects must be supplied in their entirety.
    """
    # Example only; not implemented
    # Remove the pragma: no-cover when this is implemented
    return AuthzPermissionsCheckPostResponse(
        actor_id=permissions_check_request.actor.id,
        permissions_check_results=[],
        actor_has_all_permissions=False,
    )


@router.post("/permissions/check/with-lookup")
async def check_permissions_with_lookup(  # pragma: no-cover
    permissions_check_with_lookup_request: AuthzPermissionsCheckLookupPostRequest,
) -> AuthzPermissionsCheckPostResponse:
    """
    Retrieve a yes/no answer to whether an actor has all specified permissions.
    May optionally include targets.
    Actor and target objects can be looked up by Guardian using an identifier.
    """
    # Example only; not implemented
    # Remove the pragma: no-cover when this is implemented
    return AuthzPermissionsCheckPostResponse(
        actor_id=permissions_check_with_lookup_request.actor.id,
        permissions_check_results=[],
        actor_has_all_permissions=False,
    )


@router.post("/permissions/custom/{app_name}/{namespace_name}/{endpoint_name}")
async def custom_permissions_endpoint(  # pragma: no-cover
    app_name: str,
    namespace_name: str,
    endpoint_name: str,
    custom_endpoint_request: AuthzCustomEndpointPostRequest,
) -> AuthzCustomEndpointPostResponse:
    """
    Perform a custom permissions check.
    Data supplied to this endpoint is variable, and is dependent on the endpoint.
    """
    # Example only; not implemented
    # Remove the pragma: no-cover when this is implemented
    return AuthzCustomEndpointPostResponse()
