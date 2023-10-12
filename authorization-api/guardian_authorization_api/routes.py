# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only


from fastapi import APIRouter, Depends
from guardian_lib.adapter_registry import port_dep
from guardian_lib.ports import ActorIdentifierPort

from . import business_logic
from .adapters.api import (
    FastAPICheckPermissionsAPIAdapter,
    FastAPIGetPermissionsAPIAdapter,
)
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
from .ports import (
    CheckPermissionsAPIPort,
    GetPermissionsAPIPort,
    PersistencePort,
    PolicyPort,
)

router = APIRouter()


@router.post("/permissions")
async def get_permissions(
    permissions_fetch_request: AuthzPermissionsPostRequest,
    get_permission_api: FastAPIGetPermissionsAPIAdapter = Depends(
        port_dep(GetPermissionsAPIPort, FastAPIGetPermissionsAPIAdapter)
    ),
    policy_port: PolicyPort = Depends(port_dep(PolicyPort)),
) -> AuthzPermissionsPostResponse:  # pragma no cover
    """
    Retrieve a list of permissions for an actor, with optional targets.
    Actor and target objects must be supplied in their entirety.
    """
    return await business_logic.get_permissions(
        permissions_fetch_request,
        get_permission_api,
        policy_port,
    )


@router.post("/permissions/with-lookup")
async def get_permissions_with_lookup(
    permissions_with_lookup_request: AuthzPermissionsLookupPostRequest,
    get_permission_api: FastAPIGetPermissionsAPIAdapter = Depends(
        port_dep(GetPermissionsAPIPort, FastAPIGetPermissionsAPIAdapter)
    ),
    policy_port: PolicyPort = Depends(port_dep(PolicyPort)),
    persistence_port: PersistencePort = Depends(port_dep(PersistencePort)),
    actor: ActorIdentifierPort = Depends(
        port_dep(ActorIdentifierPort).fastapi_dependency
    ),
) -> AuthzPermissionsPostResponse:
    """
    Retrieve a list of permissions for an actor, with optional targets.
    Actor and target objects can be looked up by Guardian using an identifier.
    """
    raise Exception(actor)
    return await business_logic.get_permissions_with_lookup(
        permissions_with_lookup_request,
        get_permission_api,
        policy_port,
        persistence_port,
    )


@router.post("/permissions/check")
async def check_permissions(
    permissions_check_request: AuthzPermissionsCheckPostRequest,
    check_permission_api: CheckPermissionsAPIPort = Depends(
        port_dep(CheckPermissionsAPIPort, FastAPICheckPermissionsAPIAdapter)
    ),
    policy_port: PolicyPort = Depends(port_dep(PolicyPort)),
) -> AuthzPermissionsCheckPostResponse:
    """
    Retrieve a yes/no answer to whether an actor has the specified permissions.

    Permissions passed via targeted_permissions_to_check are tested with respect
    to the provided targets.

    For permissions passed via general_permissions_to_check the targets are ignored.

    Actor and target objects must be supplied in their entirety.

    With actor_has_all_general_permissions and actor_has_all_targeted_permissions the response
    includes a separate answer for both permission types.
    """
    return await business_logic.check_permissions(
        permissions_check_request=permissions_check_request,
        check_permissions_api_port=check_permission_api,
        policy_port=policy_port,
    )


@router.post("/permissions/check/with-lookup")
async def check_permissions_with_lookup(
    permissions_check_with_lookup_request: AuthzPermissionsCheckLookupPostRequest,
    check_permissions_port: CheckPermissionsAPIPort = Depends(
        port_dep(CheckPermissionsAPIPort, FastAPICheckPermissionsAPIAdapter)
    ),
    policy_port: PolicyPort = Depends(port_dep(PolicyPort)),
    persistence_port: PersistencePort = Depends(port_dep(PersistencePort)),
) -> AuthzPermissionsCheckPostResponse:
    """
    Retrieve a yes/no answer to whether an actor has all specified permissions.
    May optionally include targets.
    Actor and target objects can be looked up by Guardian using an identifier.
    """
    return await business_logic.check_permissions_with_lookup(
        permissions_check_with_lookup_request,
        check_permissions_port,
        policy_port,
        persistence_port,
    )


@router.post("/permissions/custom/{app_name}/{namespace_name}/{endpoint_name}")
async def custom_permissions_endpoint(
    app_name: str,
    namespace_name: str,
    endpoint_name: str,
    custom_endpoint_request: AuthzCustomEndpointPostRequest,
) -> AuthzCustomEndpointPostResponse:  # pragma: no cover
    """
    Perform a custom permissions check.
    Data supplied to this endpoint is variable, and is dependent on the endpoint.
    """
    # Example only; not implemented
    # Remove the pragma: no-cover when this is implemented
    return AuthzCustomEndpointPostResponse()
