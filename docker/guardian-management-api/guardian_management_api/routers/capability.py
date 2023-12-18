# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from fastapi import APIRouter, Depends, Request
from guardian_lib.adapter_registry import port_dep
from guardian_lib.ports import AuthenticationPort
from starlette import status

from guardian_management_api import business_logic
from guardian_management_api.adapters.capability import FastAPICapabilityAPIAdapter
from guardian_management_api.models.routers.base import (
    GetAllRequest,
    GetByNamespaceRequest,
    GetFullIdentifierRequest,
)
from guardian_management_api.models.routers.capability import (
    CapabilitiesGetByRoleRequest,
    CapabilityCreateRequest,
    CapabilityEditRequest,
    CapabilityMultipleResponse,
    CapabilitySingleResponse,
)
from guardian_management_api.ports.bundle_server import BundleServerPort
from guardian_management_api.ports.capability import (
    CapabilityAPIPort,
    CapabilityPersistencePort,
)

from ..ports.authz import ResourceAuthorizationPort

router = APIRouter(tags=["capability"])


@router.get("/capabilities/{app_name}/{namespace_name}/{name}")
async def get_capability(
    request: Request,
    request_data: GetFullIdentifierRequest = Depends(),
    api_port: FastAPICapabilityAPIAdapter = Depends(
        port_dep(CapabilityAPIPort, FastAPICapabilityAPIAdapter)
    ),
    persistence_port: CapabilityPersistencePort = Depends(
        port_dep(CapabilityPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> CapabilitySingleResponse:
    return await business_logic.get_capability(
        request_data, api_port, persistence_port, authc_port, authz_port, request
    )


@router.get("/capabilities/{app_name}/{namespace_name}")
async def get_capabilities_by_namespace(
    request: Request,
    request_data: GetByNamespaceRequest = Depends(),
    api_port: FastAPICapabilityAPIAdapter = Depends(
        port_dep(CapabilityAPIPort, FastAPICapabilityAPIAdapter)
    ),
    persistence_port: CapabilityPersistencePort = Depends(
        port_dep(CapabilityPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> CapabilityMultipleResponse:
    return await business_logic.get_capabilities(
        request_data, api_port, persistence_port, authc_port, authz_port, request
    )


@router.get("/capabilities")
async def get_all_capabilities(
    request: Request,
    request_data: GetAllRequest = Depends(),
    api_port: FastAPICapabilityAPIAdapter = Depends(
        port_dep(CapabilityAPIPort, FastAPICapabilityAPIAdapter)
    ),
    persistence_port: CapabilityPersistencePort = Depends(
        port_dep(CapabilityPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> CapabilityMultipleResponse:
    return await business_logic.get_capabilities(
        request_data, api_port, persistence_port, authc_port, authz_port, request
    )


@router.get("/roles/{app_name}/{namespace_name}/{name}/capabilities")
async def get_capabilities_by_role(
    request: Request,
    request_data: CapabilitiesGetByRoleRequest = Depends(),
    api_port: FastAPICapabilityAPIAdapter = Depends(
        port_dep(CapabilityAPIPort, FastAPICapabilityAPIAdapter)
    ),
    persistence_port: CapabilityPersistencePort = Depends(
        port_dep(CapabilityPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> CapabilityMultipleResponse:
    return await business_logic.get_capabilities(
        request_data, api_port, persistence_port, authc_port, authz_port, request
    )


@router.post("/capabilities/{app_name}/{namespace_name}", status_code=201)
async def create_capability(
    request: Request,
    request_data: CapabilityCreateRequest = Depends(),
    api_port: FastAPICapabilityAPIAdapter = Depends(
        port_dep(CapabilityAPIPort, FastAPICapabilityAPIAdapter)
    ),
    persistence_port: CapabilityPersistencePort = Depends(
        port_dep(CapabilityPersistencePort)
    ),
    bundle_server_port: BundleServerPort = Depends(port_dep(BundleServerPort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> CapabilitySingleResponse:
    return await business_logic.create_capability(
        request_data,
        api_port,
        bundle_server_port,
        persistence_port,
        authc_port,
        authz_port,
        request,
    )


@router.put("/capabilities/{app_name}/{namespace_name}/{name}")
async def update_capability(
    request: Request,
    request_data: CapabilityEditRequest = Depends(),
    api_port: FastAPICapabilityAPIAdapter = Depends(
        port_dep(CapabilityAPIPort, FastAPICapabilityAPIAdapter)
    ),
    persistence_port: CapabilityPersistencePort = Depends(
        port_dep(CapabilityPersistencePort)
    ),
    bundle_server_port: BundleServerPort = Depends(port_dep(BundleServerPort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> CapabilitySingleResponse:
    return await business_logic.update_capability(
        request_data,
        api_port,
        bundle_server_port,
        persistence_port,
        authc_port,
        authz_port,
        request,
    )


@router.delete(
    "/capabilities/{app_name}/{namespace_name}/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_capability(
    request: Request,
    request_data: GetFullIdentifierRequest = Depends(),
    api_port: FastAPICapabilityAPIAdapter = Depends(
        port_dep(CapabilityAPIPort, FastAPICapabilityAPIAdapter)
    ),
    persistence_port: CapabilityPersistencePort = Depends(
        port_dep(CapabilityPersistencePort)
    ),
    bundle_server_port: BundleServerPort = Depends(port_dep(BundleServerPort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> None:
    return await business_logic.delete_capability(
        request_data,
        api_port,
        bundle_server_port,
        persistence_port,
        authc_port,
        authz_port,
        request,
    )
