# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends
from fastapi.params import Body
from fastapi.responses import ORJSONResponse
from starlette import status

from .. import business_logic
from ..adapter_registry import port_dep
from ..adapters.app import FastAPIAppAPIAdapter
from ..constants import COMPLETE_URL
from ..models.routers.app import (
    App as ResponseApp,
)
from ..models.routers.app import (
    AppAdmin as ResponseAppAdmin,
)
from ..models.routers.app import (
    AppCreateRequest,
    AppEditRequest,
    AppGetRequest,
    AppMultipleResponse,
    AppsGetRequest,
    AppSingleResponse,
)
from ..models.routers.role import Role as ResponseRole
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
    response: AppSingleResponse | None = await business_logic.get_app(
        api_request=app_get_request,
        app_api_port=management_app_api,
        persistence_port=persistence,
    )
    if response is None:
        return ORJSONResponse(  # type: ignore
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "App not found"}
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


@router.post("/apps/register", response_model=AppSingleResponse)
async def register_app():  # pragma: no cover
    """
    Register an app.

    This will also create an admin role to administrate the app.
    """
    response = AppSingleResponse(
        app=ResponseApp(
            name="my-app",
            display_name="My App",
            resource_url=f"{COMPLETE_URL}/guardian/management/apps/my-app",
            app_admin=ResponseAppAdmin(
                name="my-admin",
                display_name="My Admin",
                role=ResponseRole(
                    app_name="my-app",
                    name="my-role",
                    display_name="My Role",
                    namespace_name="my-namespace",
                    resource_url=f"{COMPLETE_URL}/roles/my-app/my-namespace/my-role",
                ),
            ),
        )
    ).dict()
    return response


@router.patch("/apps/{name}", response_model=AppSingleResponse)
async def edit_app(app_edit_request: AppEditRequest = Depends()):  # pragma: no cover
    """
    Update an app.
    """
    return AppSingleResponse(
        app=ResponseApp(
            name="my-app",
            display_name="My App",
            resource_url=f"{COMPLETE_URL}/guardian/management/apps/my-app",
            app_admin=None,
        )
    ).dict()
