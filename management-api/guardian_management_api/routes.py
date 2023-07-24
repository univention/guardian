# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.params import Body

from . import business_logic
from .adapter_registry import port_dep
from .adapters.app import FastAPIAppAPIAdapter
from .models.routes import (
    ManagementAppCreateRequest,
    ManagementAppCreateResponse,
    ManagementAppGetRequest,
    ManagementAppGetResponse,
)
from .ports.app import AppAPIPort, AppPersistencePort

router = APIRouter()


@router.post("/apps")
async def create_app(
    app_create_request: Annotated[ManagementAppCreateRequest, Body()],
    management_app_api: FastAPIAppAPIAdapter = Depends(
        port_dep(AppAPIPort, FastAPIAppAPIAdapter)
    ),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
) -> ManagementAppCreateResponse:
    return await business_logic.create_app(
        api_request=app_create_request,
        management_app_api_port=management_app_api,
        persistence_port=persistence,
    )


@router.get("/apps/{name}")
async def get_app(
    app_get_request: ManagementAppGetRequest = Depends(),
    management_app_api: FastAPIAppAPIAdapter = Depends(
        port_dep(AppAPIPort, FastAPIAppAPIAdapter)
    ),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
) -> ManagementAppGetResponse | None:
    return await business_logic.get_app(
        api_request=app_get_request,
        management_app_api_port=management_app_api,
        persistence_port=persistence,
    )
