# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from fastapi import APIRouter, Depends

from ..models.routers.base import (
    GetAllRequest,
    GetByAppRequest,
    GetByNamespaceRequest,
    GetFullIdentifierRequest,
    PaginationInfo,
)
from ..models.routers.custom_endpoint import (
    CustomEndpoint as ResponseCustomEndpoint,
)
from ..models.routers.custom_endpoint import (
    CustomEndpointCreateRequest,
    CustomEndpointEditRequest,
    CustomEndpointMultipleResponse,
    CustomEndpointSingleResponse,
)

router = APIRouter(tags=["custom_endpoint"])


@router.get(
    "/custom_endpoints/{app_name}/{namespace_name}/{name}",
    response_model=CustomEndpointSingleResponse,
)
async def get_custom_endpoint(
    custom_endpoint_get_request: GetFullIdentifierRequest = Depends(),
):
    """
    Returns a custom_endpoint object identified by `app_name`, `namespace_name` and `name`.
    """
    return CustomEndpointSingleResponse(
        custom_endpoint=ResponseCustomEndpoint(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-custom_endpoint",
            display_name="My Custom Endpoint",
            resource_url="http://fqdn/guardian/management/custom_endpoints/my-app/my-namespace/my-custom_endpoint",
            documentation="Some dummy custom endpoint.",
        )
    ).dict()


@router.get("/custom_endpoints", response_model=CustomEndpointMultipleResponse)
async def get_all_custom_endpoints(
    custom_endpoint_get_request: GetAllRequest = Depends(),
):
    """
    Returns a list of all custom_endpoints.
    """
    return CustomEndpointMultipleResponse(
        custom_endpoints=[
            ResponseCustomEndpoint(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-custom_endpoint",
                display_name="My Custom Endpoint",
                resource_url="http://fqdn/guardian/management/custom_endpoints/my-app/my-namespace/my-custom_endpoint",
                documentation="Some dummy custom endpoint.",
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.get(
    "/custom_endpoints/{app_name}", response_model=CustomEndpointMultipleResponse
)
async def get_custom_endpoints_by_app(
    custom_endpoint_get_request: GetByAppRequest = Depends(),
):
    """
    Returns a list of all custom_endpoints that belong to `app_name`.
    """
    return CustomEndpointMultipleResponse(
        custom_endpoints=[
            ResponseCustomEndpoint(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-custom_endpoint",
                display_name="My Custom Endpoint",
                resource_url="http://fqdn/guardian/management/custom_endpoints/my-app/my-namespace/my-custom_endpoint",
                documentation="Some dummy custom endpoint.",
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.get(
    "/custom_endpoints/{app_name}/{namespace_name}",
    response_model=CustomEndpointMultipleResponse,
)
async def get_custom_endpoints_by_namespace(
    custom_endpoint_get_request: GetByNamespaceRequest = Depends(),
):
    """
    Returns a list of all custom_endpoints that belong to `namespace_name` under `app_name`.
    """
    return CustomEndpointMultipleResponse(
        custom_endpoints=[
            ResponseCustomEndpoint(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-custom_endpoint",
                display_name="My Custom Endpoint",
                resource_url="http://fqdn/guardian/management/custom_endpoints/my-app/my-namespace/my-custom_endpoint",
                documentation="Some dummy custom endpoint.",
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.post(
    "/custom_endpoints/{app_name}/{namespace_name}",
    response_model=CustomEndpointSingleResponse,
)
async def create_custom_endpoint(
    custom_endpoint_create_request: CustomEndpointCreateRequest = Depends(),
):
    """
    Create a custom_endpoint.
    """
    return CustomEndpointSingleResponse(
        custom_endpoint=ResponseCustomEndpoint(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-custom_endpoint",
            display_name="My Custom Endpoint",
            resource_url="http://fqdn/guardian/management/custom_endpoints/my-app/my-namespace/my-custom_endpoint",
            documentation="Some dummy custom endpoint.",
        )
    ).dict()


@router.patch(
    "/custom_endpoints/{app_name}/{namespace_name}/{name}",
    response_model=CustomEndpointSingleResponse,
)
async def edit_custom_endpoint(
    custom_endpoint_edit_request: CustomEndpointEditRequest = Depends(),
):
    """
    Update a custom_endpoint.
    """
    return CustomEndpointSingleResponse(
        custom_endpoint=ResponseCustomEndpoint(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-custom_endpoint",
            display_name="My Custom Endpoint",
            resource_url="http://fqdn/guardian/management/custom_endpoints/my-app/my-namespace/my-custom_endpoint",
            documentation="Some dummy custom endpoint.",
        )
    ).dict()
