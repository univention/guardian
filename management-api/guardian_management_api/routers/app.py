# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from guardian_lib.adapter_registry import port_dep
from guardian_lib.ports import AuthenticationPort
from loguru import logger

from .. import business_logic
from ..adapters.app import FastAPIAppAPIAdapter
from ..models.routers.app import (
    AppCreateRequest,
    AppEditRequest,
    AppGetRequest,
    AppMultipleResponse,
    AppRegisterResponse,
    AppsGetRequest,
    AppSingleResponse,
)
from ..ports.app import AppAPIPort, AppPersistencePort
from ..ports.authz import ResourceAuthorizationPort
from ..ports.bundle_server import BundleServerPort
from ..ports.capability import CapabilityPersistencePort
from ..ports.namespace import NamespacePersistencePort
from ..ports.role import RolePersistencePort

router = APIRouter(tags=["app"])


@router.get("/apps/{name}", response_model=AppSingleResponse)
async def get_app(
    request: Request,
    app_get_request: AppGetRequest = Depends(),
    management_app_api: FastAPIAppAPIAdapter = Depends(
        port_dep(AppAPIPort, FastAPIAppAPIAdapter)
    ),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    """
    Returns an app identified by `name`
    """
    response: AppSingleResponse = await business_logic.get_app(
        api_request=app_get_request,
        app_api_port=management_app_api,
        persistence_port=persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )
    return response.model_dump()


@router.get("/apps", response_model=AppMultipleResponse)
async def get_all_apps(
    request: Request,
    app_get_request: AppsGetRequest = Depends(),
    app_api: FastAPIAppAPIAdapter = Depends(port_dep(AppAPIPort, FastAPIAppAPIAdapter)),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    """
    Returns all apps.
    """
    response: AppMultipleResponse = await business_logic.get_apps(
        api_request=app_get_request,
        app_api_port=app_api,
        persistence_port=persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )

    return response.model_dump()


@router.post(
    "/apps",
    response_model=AppSingleResponse,
    status_code=201,
)
async def create_app(
    request: Request,
    app_create_request: AppCreateRequest,
    app_api: FastAPIAppAPIAdapter = Depends(port_dep(AppAPIPort, FastAPIAppAPIAdapter)),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    response: AppSingleResponse = await business_logic.create_app(
        api_request=app_create_request,
        app_api_port=app_api,
        persistence_port=persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )
    return response.model_dump()


@router.post("/apps/register", response_model=AppRegisterResponse, status_code=201)
async def register_app(
    request: Request,
    request_data: AppCreateRequest,
    api_port: FastAPIAppAPIAdapter = Depends(
        port_dep(AppAPIPort, FastAPIAppAPIAdapter)
    ),
    app_persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
    namespace_persistence: NamespacePersistencePort = Depends(
        port_dep(NamespacePersistencePort)
    ),
    role_persistence: RolePersistencePort = Depends(port_dep(RolePersistencePort)),
    cap_persistence: CapabilityPersistencePort = Depends(
        port_dep(CapabilityPersistencePort)
    ),
    bundle_server_port: BundleServerPort = Depends(port_dep(BundleServerPort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
):  # pragma: no cover
    """
    Register an app.

    This will also create an admin role to administrate the app.
    """
    logger.bind(request_data=request_data).debug("Register app route.")
    response: AppRegisterResponse = await business_logic.register_app(
        request_data,
        api_port,
        app_persistence,
        namespace_persistence,
        role_persistence,
        cap_persistence,
        bundle_server_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )
    return response.model_dump()


@router.patch("/apps/{name}", response_model=AppSingleResponse)
async def edit_app(
    request: Request,
    app_edit_request: AppEditRequest = Depends(),
    app_api: FastAPIAppAPIAdapter = Depends(port_dep(AppAPIPort, FastAPIAppAPIAdapter)),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:  # pragma: no cover
    """
    Update an app.
    """
    return (
        await business_logic.edit_app(
            api_request=app_edit_request,
            app_api_port=app_api,
            persistence_port=persistence,
            authc_port=authc_port,
            authz_port=authz_port,
            request=request,
        )
    ).model_dump()
