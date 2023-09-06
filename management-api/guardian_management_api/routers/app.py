# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends
from fastapi.params import Body
from guardian_lib.adapter_registry import port_dep

from .. import business_logic
from ..adapters.app import FastAPIAppAPIAdapter
from ..constants import COMPLETE_URL
from ..models.routers.app import (
    App as ResponseApp,
)
from ..models.routers.app import (
    AppAdmin,
    AppCreateRequest,
    AppDefaultNamespace,
    AppEditRequest,
    AppGetRequest,
    AppMultipleResponse,
    AppRegisterResponse,
    AppsGetRequest,
    AppSingleResponse,
)
from ..models.routers.base import ManagementObjectName
from ..ports.app import AppAPIPort, AppPersistencePort

router = APIRouter(tags=["app"])


@router.get("/apps/{name}", response_model=AppSingleResponse)
async def get_app(
    app_get_request: AppGetRequest = Depends(),
    management_app_api: FastAPIAppAPIAdapter = Depends(
        port_dep(AppAPIPort, FastAPIAppAPIAdapter)
    ),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
) -> Dict[str, Any]:
    """
    Returns an app identified by `name`
    """
    response: AppSingleResponse = await business_logic.get_app(
        api_request=app_get_request,
        app_api_port=management_app_api,
        persistence_port=persistence,
    )
    return response.dict()


@router.get("/apps", response_model=AppMultipleResponse)
async def get_all_apps(
    app_get_request: AppsGetRequest = Depends(),
    app_api: FastAPIAppAPIAdapter = Depends(port_dep(AppAPIPort, FastAPIAppAPIAdapter)),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
) -> Dict[str, Any]:
    """
    Returns all apps.
    """
    response: AppMultipleResponse = await business_logic.get_apps(
        api_request=app_get_request,
        app_api_port=app_api,
        persistence_port=persistence,
    )

    return response.dict()


@router.post("/apps", response_model=AppSingleResponse)
async def create_app(
    app_create_request: Annotated[AppCreateRequest, Body()],
    app_api: FastAPIAppAPIAdapter = Depends(port_dep(AppAPIPort, FastAPIAppAPIAdapter)),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
) -> Dict[str, Any]:
    response: AppSingleResponse = await business_logic.create_app(
        api_request=app_create_request,
        app_api_port=app_api,
        persistence_port=persistence,
    )
    return response.dict()


@router.post("/apps/register", response_model=AppRegisterResponse)
async def register_app():  # pragma: no cover
    """
    Register an app.

    This will also create an admin role to administrate the app.
    """
    response = AppRegisterResponse(
        app=ResponseApp(
            name=ManagementObjectName("my-app"),
            display_name="My App",
            resource_url=f"{COMPLETE_URL}/guardian/management/apps/my-app",
        ),
        admin_role=AppAdmin(
            app_name=ManagementObjectName("my-app"),
            namespace_name=ManagementObjectName("default"),
            name=ManagementObjectName("my-admin"),
            display_name="My Admin",
            resource_url=f"{COMPLETE_URL}/roles/my-app/default/my-admin",
        ),
        default_namespace=AppDefaultNamespace(
            app_name=ManagementObjectName("my-app"),
            name=ManagementObjectName("default"),
            display_name="My App Default Namespace",
            resource_url=f"{COMPLETE_URL}/namespaces/my-app/default",
        ),
    ).dict()
    return response


@router.patch("/apps/{name}", response_model=AppSingleResponse, status_code=201)
async def edit_app(
    app_edit_request: AppEditRequest = Depends(),
    app_api: FastAPIAppAPIAdapter = Depends(port_dep(AppAPIPort, FastAPIAppAPIAdapter)),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
) -> Dict[str, Any]:  # pragma: no cover
    """
    Update an app.
    """
    return (
        await business_logic.edit_app(
            api_request=app_edit_request,
            app_api_port=app_api,
            persistence_port=persistence,
        )
    ).dict()
