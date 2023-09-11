# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Any

from fastapi import APIRouter, Depends
from guardian_lib.adapter_registry import port_dep

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
from ..ports.permission import PermissionAPIPort, PermissionPersistencePort

router = APIRouter(tags=["permission"])


@router.get(
    "/permissions/{app_name}/{namespace_name}/{name}",
    response_model=PermissionSingleResponse,
)
async def get_permission(
    permission_get_request: PermissionGetRequest = Depends(),
    api_port: FastAPIPermissionAPIAdapter = Depends(
        port_dep(PermissionAPIPort, FastAPIPermissionAPIAdapter)
    ),
    persistence_port: PermissionPersistencePort = Depends(
        port_dep(PermissionPersistencePort)
    ),
) -> PermissionSingleResponse:
    """
    Returns a permission object identified by `app_name`, `namespace_name` and `name`.
    """
    return await business_logic.get_permission(
        permission_get_request, api_port, persistence_port
    )


@router.get("/permissions", response_model=PermissionMultipleResponse)
async def get_all_permissions(
    permission_get_request: GetAllRequest = Depends(),
    api_port: FastAPIPermissionAPIAdapter = Depends(
        port_dep(PermissionAPIPort, FastAPIPermissionAPIAdapter)
    ),
    persistence_port: PermissionPersistencePort = Depends(
        port_dep(PermissionPersistencePort)
    ),
) -> PermissionMultipleResponse:
    """
    Returns a list of all permissions.
    """
    return await business_logic.get_permissions(
        permission_get_request, api_port, persistence_port
    )


@router.get("/permissions/{app_name}", response_model=PermissionMultipleResponse)
async def get_permissions_by_app(
    permission_get_request: GetByAppRequest = Depends(),
    api_port: FastAPIPermissionAPIAdapter = Depends(
        port_dep(PermissionAPIPort, FastAPIPermissionAPIAdapter)
    ),
    persistence_port: PermissionPersistencePort = Depends(
        port_dep(PermissionPersistencePort)
    ),
) -> PermissionMultipleResponse:
    """
    Returns a list of all permissions.
    """
    return await business_logic.get_permissions(
        permission_get_request, api_port, persistence_port
    )


@router.get(
    "/permissions/{app_name}/{namespace_name}",
    response_model=PermissionMultipleResponse,
)
async def get_permissions_by_namespace(
    permission_get_request: GetByNamespaceRequest = Depends(),
    api_port: FastAPIPermissionAPIAdapter = Depends(
        port_dep(PermissionAPIPort, FastAPIPermissionAPIAdapter)
    ),
    persistence_port: PermissionPersistencePort = Depends(
        port_dep(PermissionPersistencePort)
    ),
) -> PermissionMultipleResponse:
    """
    Returns a list of all permissions that belong to `namespace_name` under `app_name`.
    """
    return await business_logic.get_permissions(
        permission_get_request, api_port, persistence_port
    )


@router.post(
    "/permissions/{app_name}/{namespace_name}",
    response_model=PermissionSingleResponse,
    status_code=201,
)
async def create_permission(
    permission_create_request: PermissionCreateRequest = Depends(),
    permission_api: FastAPIPermissionAPIAdapter = Depends(
        port_dep(PermissionAPIPort, FastAPIPermissionAPIAdapter)
    ),
    persistence: PermissionPersistencePort = Depends(
        port_dep(PermissionPersistencePort)
    ),
) -> dict[str, Any]:
    """
    Create a permission.
    """
    response: PermissionSingleResponse = await business_logic.create_permission(
        api_request=permission_create_request,
        api_port=permission_api,
        persistence_port=persistence,
    )
    return response.dict()


@router.patch(
    "/permissions/{app_name}/{namespace_name}/{name}",
    response_model=PermissionSingleResponse,
)
async def edit_permission(
    permission_edit_request: PermissionEditRequest = Depends(),
    permission_api: FastAPIPermissionAPIAdapter = Depends(
        port_dep(PermissionAPIPort, FastAPIPermissionAPIAdapter)
    ),
    persistence: PermissionPersistencePort = Depends(
        port_dep(PermissionPersistencePort)
    ),
):
    """
    Edit a permission.
    """
    response: PermissionSingleResponse = await business_logic.edit_permission(
        api_request=permission_edit_request,
        api_port=permission_api,
        persistence_port=persistence,
    )
    return response.dict()
