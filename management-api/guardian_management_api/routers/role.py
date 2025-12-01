# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from guardian_lib.adapter_registry import port_dep
from guardian_lib.ports import AuthenticationPort

from guardian_management_api import business_logic

from ..adapters.role import FastAPIRoleAPIAdapter
from ..models.routers.role import (
    RoleCreateRequest,
    RoleEditRequest,
    RoleGetAllRequest,
    RoleGetByAppRequest,
    RoleGetByNamespaceRequest,
    RoleGetFullIdentifierRequest,
    RoleMultipleResponse,
    RoleSingleResponse,
)
from ..ports.authz import ResourceAuthorizationPort
from ..ports.role import RoleAPIPort, RolePersistencePort

router = APIRouter(tags=["role"])


@router.get(
    "/roles/{app_name}/{namespace_name}/{name}", response_model=RoleSingleResponse
)
async def get_role(
    request: Request,
    role_get_request: RoleGetFullIdentifierRequest = Depends(),
    management_role_api: RoleAPIPort = Depends(
        port_dep(RoleAPIPort, FastAPIRoleAPIAdapter)
    ),
    persistence: RolePersistencePort = Depends(port_dep(RolePersistencePort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    """
    Returns a role object identified by `app_name`, `namespace_name` and `name`.
    """
    response: RoleSingleResponse = await business_logic.get_role(
        api_request=role_get_request,
        role_api_port=management_role_api,
        persistence_port=persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )

    return response.model_dump()


@router.get("/roles", response_model=RoleMultipleResponse)
async def get_all_roles(
    request: Request,
    role_get_request: RoleGetAllRequest = Depends(),
    management_role_api: RoleAPIPort = Depends(
        port_dep(RoleAPIPort, FastAPIRoleAPIAdapter)
    ),
    persistence: RolePersistencePort = Depends(port_dep(RolePersistencePort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    """
    Returns a list of all roles.
    """
    response: RoleMultipleResponse = await business_logic.get_roles(
        api_request=role_get_request,
        role_api_port=management_role_api,
        persistence_port=persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )

    return response.model_dump()


@router.get("/roles/{app_name}", response_model=RoleMultipleResponse)
async def get_roles_by_app(
    request: Request,
    role_get_request: RoleGetByAppRequest = Depends(),
    management_role_api: RoleAPIPort = Depends(
        port_dep(RoleAPIPort, FastAPIRoleAPIAdapter)
    ),
    persistence: RolePersistencePort = Depends(port_dep(RolePersistencePort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    """
    Returns a list of all roles that belong to `app_name`.
    """
    response: RoleMultipleResponse = await business_logic.get_roles(
        api_request=role_get_request,
        role_api_port=management_role_api,
        persistence_port=persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )

    return response.model_dump()


@router.get("/roles/{app_name}/{namespace_name}", response_model=RoleMultipleResponse)
async def get_roles_by_namespace(
    request: Request,
    role_get_request: RoleGetByNamespaceRequest = Depends(),
    management_role_api: RoleAPIPort = Depends(
        port_dep(RoleAPIPort, FastAPIRoleAPIAdapter)
    ),
    persistence: RolePersistencePort = Depends(port_dep(RolePersistencePort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    """
    Returns a list of all roles that belong to `namespace_name` under `app_name`.
    """
    response: RoleMultipleResponse = await business_logic.get_roles(
        api_request=role_get_request,
        role_api_port=management_role_api,
        persistence_port=persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )

    return response.model_dump()


@router.post(
    "/roles/{app_name}/{namespace_name}",
    response_model=RoleSingleResponse,
    status_code=201,
)
async def create_role(
    request: Request,
    role_create_request: RoleCreateRequest = Depends(),
    management_role_api: RoleAPIPort = Depends(
        port_dep(RoleAPIPort, FastAPIRoleAPIAdapter)
    ),
    persistence: RolePersistencePort = Depends(port_dep(RolePersistencePort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    """
    Create a role.
    """
    response: RoleSingleResponse = await business_logic.create_role(
        api_request=role_create_request,
        role_api_port=management_role_api,
        persistence_port=persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )
    return response.model_dump()


@router.patch(
    "/roles/{app_name}/{namespace_name}/{name}", response_model=RoleSingleResponse
)
async def edit_role(
    request: Request,
    role_edit_request: RoleEditRequest = Depends(),
    management_role_api: RoleAPIPort = Depends(
        port_dep(RoleAPIPort, FastAPIRoleAPIAdapter)
    ),
    persistence: RolePersistencePort = Depends(port_dep(RolePersistencePort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    """
    Update a role.
    """
    response: RoleSingleResponse = await business_logic.edit_role(
        api_request=role_edit_request,
        role_api_port=management_role_api,
        persistence_port=persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )

    return response.model_dump()
