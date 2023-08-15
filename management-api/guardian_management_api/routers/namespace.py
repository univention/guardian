# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from fastapi import APIRouter, Depends

from ..models.routers.base import GetAllRequest, GetByAppRequest, PaginationInfo
from ..models.routers.namespace import (
    Namespace,
    NamespaceCreateRequest,
    NamespaceEditRequest,
    NamespaceGetRequest,
    NamespaceMultipleResponse,
    NamespaceSingleResponse,
)

router = APIRouter(tags=["namespace"])


@router.get("/namespaces/{app_name}/{name}", response_model=NamespaceSingleResponse)
async def get_namespace(namespace_get_request: NamespaceGetRequest = Depends()):
    """
    Returns a namespace object identified by `app_name` and `name`.
    """
    return NamespaceSingleResponse(
        namespace=Namespace(
            name="my-namespace",
            app_name="my-app",
            display_name="My Namespace",
            resource_url="https://fqdn/guardian/management/namespaces/my-app/my-namespace",
        )
    ).dict()


@router.get("/namespaces", response_model=NamespaceMultipleResponse)
async def get_all_namespaces(namespace_get_request: GetAllRequest = Depends()):
    """
    Returns a list of all namespaces.
    """
    return NamespaceMultipleResponse(
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
        namespaces=[
            Namespace(
                name="my-namespace",
                app_name="my-app",
                display_name="My Namespace",
                resource_url="https://fqdn/guardian/management/namespaces/my-app/my-namespace",
            )
        ],
    ).dict()


@router.get("/namespaces/{app_name}", response_model=NamespaceMultipleResponse)
async def get_namespaces_by_app(
    namespace_get_request: GetByAppRequest = Depends(),
):
    """
    Returns a list of all namespaces that belong to `app_name`.
    """
    return NamespaceMultipleResponse(
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
        namespaces=[
            Namespace(
                name="my-namespace",
                app_name="my-app",
                display_name="My Namespace",
                resource_url="https://fqdn/guardian/management/namespaces/my-app/my-namespace",
            )
        ],
    ).dict()


@router.post("/namespaces/{app_name}", response_model=NamespaceSingleResponse)
async def create_namespace(
    namespace_create_request: NamespaceCreateRequest = Depends(),
):
    """
    Create a namespace.
    """
    return NamespaceSingleResponse(
        namespace=Namespace(
            name="my-namespace",
            app_name="my-app",
            display_name="My Namespace",
            resource_url="https://fqdn/guardian/management/namespaces/my-app/my-namespace",
        )
    ).dict()


@router.patch("/namespaces/{app_name}/{name}", response_model=NamespaceSingleResponse)
async def edit_namespace(namespace_edit_request: NamespaceEditRequest = Depends()):
    """
    Update a namespace.
    """
    return NamespaceSingleResponse(
        namespace=Namespace(
            name="my-namespace",
            app_name="my-app",
            display_name="My Namespace",
            resource_url="https://fqdn/guardian/management/namespaces/my-app/my-namespace",
        )
    ).dict()
