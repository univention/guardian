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
from ..models.routers.role import (
    Role as ResponseRole,
)
from ..models.routers.role import (
    RoleCreateRequest,
    RoleEditRequest,
    RoleMultipleResponse,
    RoleSingleResponse,
)

router = APIRouter(tags=["role"])


@router.get(
    "/roles/{app_name}/{namespace_name}/{name}", response_model=RoleSingleResponse
)
async def get_role(role_get_request: GetFullIdentifierRequest = Depends()):
    """
    Returns a role object identified by `app_name`, `namespace_name` and `name`.
    """
    return RoleSingleResponse(
        role=ResponseRole(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-role",
            display_name="My Role",
            resource_url="http://fqdn/guardian/management/roles/my-app/my-namespace/my-role",
        )
    ).dict()


@router.get("/roles", response_model=RoleMultipleResponse)
async def get_all_roles(role_get_request: GetAllRequest = Depends()):
    """
    Returns a list of all roles.
    """
    return RoleMultipleResponse(
        roles=[
            ResponseRole(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-role",
                display_name="My Role",
                resource_url="http://fqdn/guardian/management/roles/my-app/my-namespace/my-role",
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.get("/roles/{app_name}", response_model=RoleMultipleResponse)
async def get_roles_by_app(role_get_request: GetByAppRequest = Depends()):
    """
    Returns a list of all roles that belong to `app_name`.
    """
    return RoleMultipleResponse(
        roles=[
            ResponseRole(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-role",
                display_name="My Role",
                resource_url="http://fqdn/guardian/management/roles/my-app/my-namespace/my-role",
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.get("/roles/{app_name}/{namespace_name}", response_model=RoleMultipleResponse)
async def get_roles_by_namespace(role_get_request: GetByNamespaceRequest = Depends()):
    """
    Returns a list of all roles that belong to `namespace_name` under `app_name`.
    """
    return RoleMultipleResponse(
        roles=[
            ResponseRole(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-role",
                display_name="My Role",
                resource_url="http://fqdn/guardian/management/roles/my-app/my-namespace/my-role",
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.post("/roles/{app_name}/{namespace_name}", response_model=RoleSingleResponse)
async def create_role(role_create_request: RoleCreateRequest = Depends()):
    """
    Create a role.
    """
    return RoleSingleResponse(
        role=ResponseRole(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-role",
            display_name="My Role",
            resource_url="http://fqdn/guardian/management/roles/my-app/my-namespace/my-role",
        )
    ).dict()


@router.patch(
    "/roles/{app_name}/{namespace_name}/{name}", response_model=RoleSingleResponse
)
async def edit_role(role_edit_request: RoleEditRequest = Depends()):
    """
    Update a role.
    """
    return RoleSingleResponse(
        role=ResponseRole(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-role",
            display_name="My Role",
            resource_url="http://fqdn/guardian/management/roles/my-app/my-namespace/my-role",
        )
    ).dict()
