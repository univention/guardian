# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Any

from fastapi import APIRouter, Depends, Request
from guardian_lib.adapter_registry import port_dep
from guardian_lib.ports import AuthenticationPort

from .. import business_logic
from ..adapters.permission import FastAPIPermissionAPIAdapter
from ..models.routers.base import (
    GetAllRequest,
    GetByAppRequest,
    GetByNamespaceRequest,
)
from ..models.routers.permission import (
    PermissionCreateRequest,
    PermissionEditRequest,
    PermissionGetRequest,
    PermissionMultipleResponse,
    PermissionSingleResponse,
)
from ..ports.authz import ResourceAuthorizationPort
from ..ports.permission import PermissionAPIPort, PermissionPersistencePort

router = APIRouter(tags=["permission"])


@router.get(
    "/permissions/{app_name}/{namespace_name}/{name}",
    response_model=PermissionSingleResponse,
)
async def get_permission(
    request: Request,
    permission_get_request: PermissionGetRequest = Depends(),
    api_port: FastAPIPermissionAPIAdapter = Depends(
        port_dep(PermissionAPIPort, FastAPIPermissionAPIAdapter)
    ),
    persistence_port: PermissionPersistencePort = Depends(
        port_dep(PermissionPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> PermissionSingleResponse:
    """
    Returns a permission object identified by `app_name`, `namespace_name` and `name`.
    """
    return await business_logic.get_permission(
        api_request=permission_get_request,
        api_port=api_port,
        persistence_port=persistence_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )


@router.get("/permissions", response_model=PermissionMultipleResponse)
async def get_all_permissions(
    request: Request,
    permission_get_request: GetAllRequest = Depends(),
    api_port: FastAPIPermissionAPIAdapter = Depends(
        port_dep(PermissionAPIPort, FastAPIPermissionAPIAdapter)
    ),
    persistence_port: PermissionPersistencePort = Depends(
        port_dep(PermissionPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> PermissionMultipleResponse:
    """
    Returns a list of all permissions.
    """
    return await business_logic.get_permissions(
        api_request=permission_get_request,
        api_port=api_port,
        persistence_port=persistence_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )


@router.get("/permissions/{app_name}", response_model=PermissionMultipleResponse)
async def get_permissions_by_app(
    request: Request,
    permission_get_request: GetByAppRequest = Depends(),
    api_port: FastAPIPermissionAPIAdapter = Depends(
        port_dep(PermissionAPIPort, FastAPIPermissionAPIAdapter)
    ),
    persistence_port: PermissionPersistencePort = Depends(
        port_dep(PermissionPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> PermissionMultipleResponse:
    """
    Returns a list of all permissions.
    """
    return await business_logic.get_permissions(
        api_request=permission_get_request,
        api_port=api_port,
        persistence_port=persistence_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )


@router.get(
    "/permissions/{app_name}/{namespace_name}",
    response_model=PermissionMultipleResponse,
)
async def get_permissions_by_namespace(
    request: Request,
    permission_get_request: GetByNamespaceRequest = Depends(),
    api_port: FastAPIPermissionAPIAdapter = Depends(
        port_dep(PermissionAPIPort, FastAPIPermissionAPIAdapter)
    ),
    persistence_port: PermissionPersistencePort = Depends(
        port_dep(PermissionPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> PermissionMultipleResponse:
    """
    Returns a list of all permissions that belong to `namespace_name` under `app_name`.
    """
    return await business_logic.get_permissions(
        api_request=permission_get_request,
        api_port=api_port,
        persistence_port=persistence_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )


@router.post(
    "/permissions/{app_name}/{namespace_name}",
    response_model=PermissionSingleResponse,
    status_code=201,
)
async def create_permission(
    request: Request,
    permission_create_request: PermissionCreateRequest = Depends(),
    permission_api: FastAPIPermissionAPIAdapter = Depends(
        port_dep(PermissionAPIPort, FastAPIPermissionAPIAdapter)
    ),
    persistence: PermissionPersistencePort = Depends(
        port_dep(PermissionPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> dict[str, Any]:
    """
    Create a permission.
    """
    response: PermissionSingleResponse = await business_logic.create_permission(
        api_request=permission_create_request,
        api_port=permission_api,
        persistence_port=persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )
    return response.model_dump()


@router.patch(
    "/permissions/{app_name}/{namespace_name}/{name}",
    response_model=PermissionSingleResponse,
)
async def edit_permission(
    request: Request,
    permission_edit_request: PermissionEditRequest = Depends(),
    permission_api: FastAPIPermissionAPIAdapter = Depends(
        port_dep(PermissionAPIPort, FastAPIPermissionAPIAdapter)
    ),
    persistence: PermissionPersistencePort = Depends(
        port_dep(PermissionPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
):
    """
    Edit a permission.
    """
    response: PermissionSingleResponse = await business_logic.edit_permission(
        api_request=permission_edit_request,
        api_port=permission_api,
        persistence_port=persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )
    return response.model_dump()
