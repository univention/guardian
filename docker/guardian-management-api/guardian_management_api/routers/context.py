# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from guardian_lib.adapter_registry import port_dep
from guardian_lib.ports import AuthenticationPort

from .. import business_logic
from ..adapters.context import FastAPIContextAPIAdapter
from ..models.routers.base import (
    GetByAppRequest,
    GetByNamespaceRequest,
)
from ..models.routers.context import (
    ContextCreateRequest,
    ContextEditRequest,
    ContextGetRequest,
    ContextMultipleResponse,
    ContextsGetRequest,
    ContextSingleResponse,
)
from ..ports.authz import ResourceAuthorizationPort
from ..ports.context import ContextAPIPort, ContextPersistencePort

router = APIRouter(tags=["context"])


@router.get(
    "/contexts/{app_name}/{namespace_name}/{name}", response_model=ContextSingleResponse
)
async def get_context(
    request: Request,
    context_get_request: ContextGetRequest = Depends(),
    context_api: FastAPIContextAPIAdapter = Depends(
        port_dep(ContextAPIPort, FastAPIContextAPIAdapter)
    ),
    context_persistence: ContextPersistencePort = Depends(
        port_dep(ContextPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    """
    Returns a context object identified by `app_name`, `namespace_name` and `name`.
    """
    response: ContextSingleResponse = await business_logic.get_context(
        api_request=context_get_request,
        api_port=context_api,
        persistence_port=context_persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )
    return response.dict()


@router.get("/contexts", response_model=ContextMultipleResponse)
async def get_all_contexts(
    request: Request,
    context_get_request: ContextsGetRequest = Depends(),
    api_port: FastAPIContextAPIAdapter = Depends(
        port_dep(ContextAPIPort, FastAPIContextAPIAdapter)
    ),
    persistence_port: ContextPersistencePort = Depends(
        port_dep(ContextPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    """
    Returns a list of all contexts.
    """
    response: ContextMultipleResponse = await business_logic.get_contexts(
        api_request=context_get_request,
        api_port=api_port,
        persistence_port=persistence_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )
    return response.dict()


@router.get("/contexts/{app_name}", response_model=ContextMultipleResponse)
async def get_contexts_by_app(
    request: Request,
    context_get_request: GetByAppRequest = Depends(),
    api_port: FastAPIContextAPIAdapter = Depends(
        port_dep(ContextAPIPort, FastAPIContextAPIAdapter)
    ),
    persistence_port: ContextPersistencePort = Depends(
        port_dep(ContextPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    """
    Returns a list of all contexts that belong to `app_name`.
    """
    response: ContextMultipleResponse = await business_logic.get_contexts(
        api_request=context_get_request,
        api_port=api_port,
        persistence_port=persistence_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )
    return response.dict()


@router.get(
    "/contexts/{app_name}/{namespace_name}", response_model=ContextMultipleResponse
)
async def get_contexts_by_namespace(
    request: Request,
    context_get_request: GetByNamespaceRequest = Depends(),
    api_port: FastAPIContextAPIAdapter = Depends(
        port_dep(ContextAPIPort, FastAPIContextAPIAdapter)
    ),
    persistence_port: ContextPersistencePort = Depends(
        port_dep(ContextPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
):
    """
    Returns a list of all contexts that belong to `namespace_name` under `app_name`.
    """
    response: ContextMultipleResponse = await business_logic.get_contexts(
        api_request=context_get_request,
        api_port=api_port,
        persistence_port=persistence_port,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )
    return response.dict()


@router.post(
    "/contexts/{app_name}/{namespace_name}",
    response_model=ContextSingleResponse,
    status_code=201,
)
async def create_context(
    request: Request,
    context_create_request: ContextCreateRequest = Depends(),
    context_api: FastAPIContextAPIAdapter = Depends(
        port_dep(ContextAPIPort, FastAPIContextAPIAdapter)
    ),
    context_persistence: ContextPersistencePort = Depends(
        port_dep(ContextPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    """
    Create a context.
    """
    response: ContextSingleResponse = await business_logic.create_context(
        api_request=context_create_request,
        api_port=context_api,
        persistence_port=context_persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )
    return response.dict()


@router.patch(
    "/contexts/{app_name}/{namespace_name}/{name}",
    response_model=ContextSingleResponse,
)
async def edit_context(
    request: Request,
    context_edit_request: ContextEditRequest = Depends(),
    context_api: FastAPIContextAPIAdapter = Depends(
        port_dep(ContextAPIPort, FastAPIContextAPIAdapter)
    ),
    context_persistence: ContextPersistencePort = Depends(
        port_dep(ContextPersistencePort)
    ),
    authc_port: AuthenticationPort = Depends(port_dep(AuthenticationPort)),
    authz_port: ResourceAuthorizationPort = Depends(
        port_dep(ResourceAuthorizationPort)
    ),
) -> Dict[str, Any]:
    """
    Update a context.
    """
    response: ContextSingleResponse = await business_logic.edit_context(
        api_request=context_edit_request,
        api_port=context_api,
        persistence_port=context_persistence,
        authc_port=authc_port,
        authz_port=authz_port,
        request=request,
    )
    return response.dict()
