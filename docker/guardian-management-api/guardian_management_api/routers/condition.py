# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from fastapi import APIRouter, Depends, Request
from guardian_lib.adapter_registry import port_dep
from guardian_lib.ports import AuthenticationPort

from .. import business_logic
from ..adapters.condition import FastAPIConditionAPIAdapter
from ..models.routers.base import (
    GetAllRequest,
    GetByAppRequest,
    GetByNamespaceRequest,
    GetFullIdentifierRequest,
)
from ..models.routers.condition import (
    ConditionCreateRequest,
    ConditionEditRequest,
    ConditionMultipleResponse,
    ConditionSingleResponse,
)
from ..ports.authz import ResourceAuthorizationPort
from ..ports.bundle_server import BundleServerPort
from ..ports.condition import ConditionAPIPort, ConditionPersistencePort

router = APIRouter(tags=["condition"])


@router.get(
    "/conditions/{app_name}/{namespace_name}/{name}",
    response_model=ConditionSingleResponse,
)
async def get_condition(
    request: Request,
    condition_get_request: GetFullIdentifierRequest = Depends(),
    api_port: FastAPIConditionAPIAdapter = Depends(
        port_dep(ConditionAPIPort, FastAPIConditionAPIAdapter)
    ),
    persistence_port: ConditionPersistencePort = Depends(
        port_dep(ConditionPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
):
    """
    Returns a condition object identified by `app_name`, `namespace_name` and `name`.
    """
    return await business_logic.get_condition(
        api_request=condition_get_request,
        api_port=api_port,
        persistence_port=persistence_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )


@router.get("/conditions", response_model=ConditionMultipleResponse)
async def get_all_conditions(
    request: Request,
    condition_get_request: GetAllRequest = Depends(),
    api_port: FastAPIConditionAPIAdapter = Depends(
        port_dep(ConditionAPIPort, FastAPIConditionAPIAdapter)
    ),
    persistence_port: ConditionPersistencePort = Depends(
        port_dep(ConditionPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
):
    """
    Returns a list of all conditions.
    """
    return await business_logic.get_conditions(
        api_request=condition_get_request,
        api_port=api_port,
        persistence_port=persistence_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )


@router.get("/conditions/{app_name}", response_model=ConditionMultipleResponse)
async def get_conditions_by_app(
    request: Request,
    condition_get_request: GetByAppRequest = Depends(),
    api_port: FastAPIConditionAPIAdapter = Depends(
        port_dep(ConditionAPIPort, FastAPIConditionAPIAdapter)
    ),
    persistence_port: ConditionPersistencePort = Depends(
        port_dep(ConditionPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
):
    """
    Returns a list of all conditions that belong to `app_name`.
    """
    return await business_logic.get_conditions(
        api_request=condition_get_request,
        api_port=api_port,
        persistence_port=persistence_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )


@router.get(
    "/conditions/{app_name}/{namespace_name}", response_model=ConditionMultipleResponse
)
async def get_conditions_by_namespace(
    request: Request,
    condition_get_request: GetByNamespaceRequest = Depends(),
    api_port: FastAPIConditionAPIAdapter = Depends(
        port_dep(ConditionAPIPort, FastAPIConditionAPIAdapter)
    ),
    persistence_port: ConditionPersistencePort = Depends(
        port_dep(ConditionPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
):
    """
    Returns a list of all conditions that belong to `namespace_name` under `app_name`.
    """
    return await business_logic.get_conditions(
        api_request=condition_get_request,
        api_port=api_port,
        persistence_port=persistence_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )


@router.post(
    "/conditions/{app_name}/{namespace_name}",
    response_model=ConditionSingleResponse,
    status_code=201,
)
async def create_condition(
    request: Request,
    condition_create_request: ConditionCreateRequest = Depends(),
    api_port: FastAPIConditionAPIAdapter = Depends(
        port_dep(ConditionAPIPort, FastAPIConditionAPIAdapter)
    ),
    persistence_port: ConditionPersistencePort = Depends(
        port_dep(ConditionPersistencePort)
    ),
    bundle_server_port: BundleServerPort = Depends(port_dep(BundleServerPort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
):
    """
    Create a condition.
    """
    return await business_logic.create_condition(
        api_request=condition_create_request,
        api_port=api_port,
        persistence_port=persistence_port,
        bundle_server_port=bundle_server_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )


@router.patch(
    "/conditions/{app_name}/{namespace_name}/{name}",
    response_model=ConditionSingleResponse,
)
async def edit_condition(
    request: Request,
    condition_edit_request: ConditionEditRequest = Depends(),
    api_port: FastAPIConditionAPIAdapter = Depends(
        port_dep(ConditionAPIPort, FastAPIConditionAPIAdapter)
    ),
    persistence_port: ConditionPersistencePort = Depends(
        port_dep(ConditionPersistencePort)
    ),
    bundle_server_port: BundleServerPort = Depends(port_dep(BundleServerPort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
):
    """
    Update a condition.
    """
    return await business_logic.update_condition(
        condition_edit_request,
        api_port=api_port,
        persistence_port=persistence_port,
        bundle_server_port=bundle_server_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )
