from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends
from fastapi.params import Body
from fastapi.responses import ORJSONResponse
from starlette import status

from .. import business_logic
from ..adapter_registry import port_dep
from ..adapters.app import FastAPIAppAPIAdapter
from ..models.routers.app import (
    AppCreateRequest,
    AppGetRequest,
    AppSingleResponse,
)
from ..ports.app import AppAPIPort, AppPersistencePort

router = APIRouter(tags=["app"])


@router.post("/apps", response_model=AppSingleResponse)
async def create_app(
    app_create_request: Annotated[AppCreateRequest, Body()],
    management_app_api: FastAPIAppAPIAdapter = Depends(
        port_dep(AppAPIPort, FastAPIAppAPIAdapter)
    ),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
) -> Dict[str, Any]:
    response: AppSingleResponse = await business_logic.create_app(
        api_request=app_create_request,
        management_app_api_port=management_app_api,
        persistence_port=persistence,
    )
    return response.dict()


@router.get("/apps/{name}", response_model=AppSingleResponse)
async def get_app(
    app_get_request: AppGetRequest = Depends(),
    management_app_api: FastAPIAppAPIAdapter = Depends(
        port_dep(AppAPIPort, FastAPIAppAPIAdapter)
    ),
    persistence: AppPersistencePort = Depends(port_dep(AppPersistencePort)),
) -> Dict[str, Any]:
    response: AppSingleResponse | None = await business_logic.get_app(
        api_request=app_get_request,
        management_app_api_port=management_app_api,
        persistence_port=persistence,
    )
    if response is None:
        return ORJSONResponse(  # type: ignore
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "App not found"}
        )
    return response.dict()
