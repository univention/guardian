# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from fastapi import APIRouter, Depends

from ..models.routers.base import (
    GetAllRequest,
    GetByAppRequest,
    GetByNamespaceRequest,
    GetFullIdentifierRequest,
    PaginationInfo,
)
from ..models.routers.permission import (
    Permission as ResponsePermission,
)
from ..models.routers.permission import (
    PermissionCreateRequest,
    PermissionEditRequest,
    PermissionMultipleResponse,
    PermissionSingleResponse,
)

router = APIRouter(tags=["permission"])


@router.get(
    "/permissions/{app_name}/{namespace_name}/{name}",
    response_model=PermissionSingleResponse,
)
async def get_permission(permission_get_request: GetFullIdentifierRequest = Depends()):
    """
    Returns a permission object identified by `app_name`, `namespace_name` and `name`.
    """
    return PermissionSingleResponse(
        permission=ResponsePermission(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-permission",
            display_name="My Permission",
            resource_url="http://fqdn/guardian/management/permissions/my-app/my-namespace/my-permission",
        )
    ).dict()


@router.get("/permissions", response_model=PermissionMultipleResponse)
async def get_all_permissions(permission_get_request: GetAllRequest = Depends()):
    """
    Returns a list of all permissions.
    """
    return PermissionMultipleResponse(
        permissions=[
            ResponsePermission(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-permission",
                display_name="My Permission",
                resource_url="http://fqdn/guardian/management/permissions/my-app/my-namespace/my-permission",
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.get("/permissions/{app_name}", response_model=PermissionMultipleResponse)
async def get_permissions_by_app(permission_get_request: GetByAppRequest = Depends()):
    """
    Returns a list of all permissions that belong to `app_name`.
    """
    return PermissionMultipleResponse(
        permissions=[
            ResponsePermission(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-permission",
                display_name="My Permission",
                resource_url="http://fqdn/guardian/management/permissions/my-app/my-namespace/my-permission",
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.get(
    "/permissions/{app_name}/{namespace_name}",
    response_model=PermissionMultipleResponse,
)
async def get_permissions_by_namespace(
    permission_get_request: GetByNamespaceRequest = Depends(),
):
    """
    Returns a list of all permissions that belong to `namespace_name` under `app_name`.
    """
    return PermissionMultipleResponse(
        permissions=[
            ResponsePermission(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-permission",
                display_name="My Permission",
                resource_url="http://fqdn/guardian/management/permissions/my-app/my-namespace/my-permission",
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.post(
    "/permissions/{app_name}/{namespace_name}", response_model=PermissionSingleResponse
)
async def create_permission(
    permission_create_request: PermissionCreateRequest = Depends(),
):
    """
    Create a permission.
    """
    return PermissionSingleResponse(
        permission=ResponsePermission(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-permission",
            display_name="My Permission",
            resource_url="http://fqdn/guardian/management/permissions/my-app/my-namespace/my-permission",
        )
    ).dict()


@router.patch(
    "/permissions/{app_name}/{namespace_name}/{name}",
    response_model=PermissionSingleResponse,
)
async def edit_permission(
    permission_edit_request: PermissionEditRequest = Depends(),
):
    """
    Create a permission.
    """
    return PermissionSingleResponse(
        permission=ResponsePermission(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-permission",
            display_name="My Permission",
            resource_url="http://fqdn/guardian/management/permissions/my-app/my-namespace/my-permission",
        )
    ).dict()
