# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from fastapi import APIRouter, Depends
from guardian_lib.adapter_registry import port_dep

from .. import business_logic
from ..adapters.context import FastAPIContextAPIAdapter
from ..models.routers.base import (
    GetAllRequest,
    GetByAppRequest,
    GetByNamespaceRequest,
    GetFullIdentifierRequest,
    PaginationInfo,
)
from ..models.routers.context import (
    Context as ResponseContext,
)
from ..models.routers.context import (
    ContextCreateRequest,
    ContextEditRequest,
    ContextMultipleResponse,
    ContextSingleResponse,
)
from ..ports.context import ContextAPIPort, ContextPersistencePort

router = APIRouter(tags=["context"])


@router.get(
    "/contexts/{app_name}/{namespace_name}/{name}", response_model=ContextSingleResponse
)
async def get_context(context_get_request: GetFullIdentifierRequest = Depends()):
    """
    Returns a context object identified by `app_name`, `namespace_name` and `name`.
    """
    return ContextSingleResponse(
        context=ResponseContext(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-context",
            display_name="My Context",
            resource_url="http://fqdn/guardian/management/contexts/my-app/my-namespace/my-context",
        )
    ).dict()


@router.get("/contexts", response_model=ContextMultipleResponse)
async def get_all_contexts(context_get_request: GetAllRequest = Depends()):
    """
    Returns a list of all contexts.
    """
    return ContextMultipleResponse(
        contexts=[
            ResponseContext(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-context",
                display_name="My Context",
                resource_url="http://fqdn/guardian/management/contexts/my-app/my-namespace/my-context",
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.get("/contexts/{app_name}", response_model=ContextMultipleResponse)
async def get_contexts_by_app(context_get_request: GetByAppRequest = Depends()):
    """
    Returns a list of all contexts that belong to `app_name`.
    """
    return ContextMultipleResponse(
        contexts=[
            ResponseContext(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-context",
                display_name="My Context",
                resource_url="http://fqdn/guardian/management/contexts/my-app/my-namespace/my-context",
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.get(
    "/contexts/{app_name}/{namespace_name}", response_model=ContextMultipleResponse
)
async def get_contexts_by_namespace(
    context_get_request: GetByNamespaceRequest = Depends(),
):
    """
    Returns a list of all contexts that belong to `namespace_name` under `app_name`.
    """
    return ContextMultipleResponse(
        contexts=[
            ResponseContext(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-context",
                display_name="My Context",
                resource_url="http://fqdn/guardian/management/contexts/my-app/my-namespace/my-context",
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.post(
    "/contexts/{app_name}/{namespace_name}", response_model=ContextSingleResponse
)
async def create_context(
    context_create_request: ContextCreateRequest = Depends(),
    context_api: FastAPIContextAPIAdapter = Depends(
        port_dep(ContextAPIPort, FastAPIContextAPIAdapter)
    ),
    context_persistence: ContextPersistencePort = Depends(
        port_dep(ContextPersistencePort)
    ),
) -> Dict[str, Any]:
    """
    Create a context.
    """
    response: ContextSingleResponse = await business_logic.create_context(
        api_request=context_create_request,
        api_port=context_api,
        persistence_port=context_persistence,
    )
    return response.dict()


@router.patch(
    "/contexts/{app_name}/{namespace_name}/{name}", response_model=ContextSingleResponse
)
async def edit_context(context_edit_request: ContextEditRequest = Depends()):
    """
    Update a context.
    """
    return ContextSingleResponse(
        context=ResponseContext(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-context",
            display_name="My Context",
            resource_url="http://fqdn/guardian/management/contexts/my-app/my-namespace/my-context",
        )
    ).dict()
