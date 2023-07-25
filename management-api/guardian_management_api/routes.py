# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.params import Body
from fastapi.responses import ORJSONResponse

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


@router.post("/apps", response_model=ManagementAppCreateResponse)
async def create_app(
    app_create_request: Annotated[ManagementAppCreateRequest, Body()],
    management_app_api: FastAPIAppAPIAdapter = Depends(
        port_dep(AppAPIPort, FastAPIAppAPIAdapter)
    ),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
):
    return ORJSONResponse(
        content=jsonable_encoder(
            await business_logic.create_app(
                api_request=app_create_request,
                management_app_api_port=management_app_api,
                persistence_port=persistence,
            )
        )
    )


@router.get("/apps/{name}", response_model=ManagementAppGetResponse | None)
async def get_app(
    app_get_request: ManagementAppGetRequest = Depends(),
    management_app_api: FastAPIAppAPIAdapter = Depends(
        port_dep(AppAPIPort, FastAPIAppAPIAdapter)
    ),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
):
    app: ManagementAppGetResponse | None = await business_logic.get_app(
        api_request=app_get_request,
        management_app_api_port=management_app_api,
        persistence_port=persistence,
    )
    if app is None:
        raise HTTPException(status_code=404, detail="App not found")
    return ORJSONResponse(content=jsonable_encoder(app))
