# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from fastapi import APIRouter, Depends
from guardian_lib.adapter_registry import port_dep

from .. import business_logic
from ..adapters.namespace import FastAPINamespaceAPIAdapter
from ..models.routers.base import GetByAppRequest
from ..models.routers.namespace import (
    NamespaceCreateRequest,
    NamespaceEditRequest,
    NamespaceGetRequest,
    NamespaceMultipleResponse,
    NamespacesGetRequest,
    NamespaceSingleResponse,
)
from ..ports.namespace import NamespaceAPIPort, NamespacePersistencePort

router = APIRouter(tags=["namespace"])


@router.get("/namespaces/{app_name}/{name}", response_model=NamespaceSingleResponse)
async def get_namespace(
    namespace_get_request: NamespaceGetRequest = Depends(),
    namespace_api: FastAPINamespaceAPIAdapter = Depends(
        port_dep(NamespaceAPIPort, FastAPINamespaceAPIAdapter)
    ),
    namespace_persistence: NamespacePersistencePort = Depends(
        port_dep(NamespacePersistencePort)
    ),
):
    """
    Returns a namespace object identified by `app_name` and `name`.
    """
    response: NamespaceSingleResponse = await business_logic.get_namespace(
        api_request=namespace_get_request,
        namespace_api_port=namespace_api,
        namespace_persistence_port=namespace_persistence,
    )
    return response.dict()


@router.get("/namespaces", response_model=NamespaceMultipleResponse)
async def get_all_namespaces(
    namespaces_get_request: NamespacesGetRequest = Depends(),
    namespace_api: FastAPINamespaceAPIAdapter = Depends(
        port_dep(NamespaceAPIPort, FastAPINamespaceAPIAdapter)
    ),
    namespace_persistence: NamespacePersistencePort = Depends(
        port_dep(NamespacePersistencePort)
    ),
):
    """
    Returns a list of all namespaces.
    """
    response: NamespaceMultipleResponse = await business_logic.get_namespaces(
        api_request=namespaces_get_request,
        namespace_api_port=namespace_api,
        namespace_persistence_port=namespace_persistence,
    )
    return response.dict()


@router.get("/namespaces/{app_name}", response_model=NamespaceMultipleResponse)
async def get_namespaces_by_app(
    namespaces_by_app_get_request: GetByAppRequest = Depends(),
    namespace_api: FastAPINamespaceAPIAdapter = Depends(
        port_dep(NamespaceAPIPort, FastAPINamespaceAPIAdapter)
    ),
    namespace_persistence: NamespacePersistencePort = Depends(
        port_dep(NamespacePersistencePort)
    ),
):
    """
    Returns a list of all namespaces that belong to `app_name`.
    """
    response: NamespaceMultipleResponse = await business_logic.get_namespaces_by_app(
        api_request=namespaces_by_app_get_request,
        namespace_api_port=namespace_api,
        namespace_persistence_port=namespace_persistence,
    )
    return response.dict()


@router.post(
    "/namespaces/{app_name}", response_model=NamespaceSingleResponse, status_code=201
)
async def create_namespace(
    namespace_create_request: NamespaceCreateRequest = Depends(),
    namespace_api: FastAPINamespaceAPIAdapter = Depends(
        port_dep(NamespaceAPIPort, FastAPINamespaceAPIAdapter)
    ),
    namespace_persistence: NamespacePersistencePort = Depends(
        port_dep(NamespacePersistencePort)
    ),
):
    """
    Create a namespace.
    """
    response: NamespaceSingleResponse = await business_logic.create_namespace(
        api_request=namespace_create_request,
        namespace_api_port=namespace_api,
        namespace_persistence_port=namespace_persistence,
    )
    return response.dict()


@router.patch(
    "/namespaces/{app_name}/{name}",
    response_model=NamespaceSingleResponse,
    status_code=201,
)
async def edit_namespace(
    namespace_edit_request: NamespaceEditRequest = Depends(),
    namespace_api: FastAPINamespaceAPIAdapter = Depends(
        port_dep(NamespaceAPIPort, FastAPINamespaceAPIAdapter)
    ),
    namespace_persistence: NamespacePersistencePort = Depends(
        port_dep(NamespacePersistencePort)
    ),
):
    """
    Update a namespace.
    """
    response: NamespaceSingleResponse = await business_logic.edit_namespace(
        api_request=namespace_edit_request,
        namespace_api_port=namespace_api,
        namespace_persistence_port=namespace_persistence,
    )
    return response.dict()
