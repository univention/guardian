# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from fastapi import APIRouter, Depends
from starlette import status

from guardian_management_api.models.routers.base import (
    GetAllRequest,
    GetByNamespaceRequest,
    GetFullIdentifierRequest,
    PaginationInfo,
)
from guardian_management_api.models.routers.capability import (
    Capability,
    CapabilityCondition,
    CapabilityCreateRequest,
    CapabilityEditRequest,
    CapabilityMultipleResponse,
    CapabilityPermission,
    CapabilityRole,
    CapabilitySingleResponse,
    RelationChoices,
)

router = APIRouter(tags=["capability"])


def create_dummy_capability():
    return Capability(
        app_name="app",
        namespace_name="namespace",
        name="capability",
        display_name="Capability",
        resource_url="https://fqdn/capabilities/app_name/namespace_name/capability",
        role=CapabilityRole(
            app_name="app",
            namespace_name="namespace",
            name="role",
        ),
        relation=RelationChoices.AND,
        conditions=[
            CapabilityCondition(
                app_name="app",
                namespace_name="namespace",
                name="condition",
            )
        ],
        permissions=[
            CapabilityPermission(
                app_name="app",
                namespace_name="namespace",
                name="capability",
            )
        ],
    )


@router.get("/capabilities/{app_name}/{namespace_name}/{name}")
def get_capability(request_data: GetFullIdentifierRequest = Depends()):
    return CapabilitySingleResponse(capability=create_dummy_capability())


@router.get("/capabilities/{app_name}/{namespace_name}")
def get_capability_by_namespace(request_data: GetByNamespaceRequest = Depends()):
    return CapabilityMultipleResponse(
        capabilities=[create_dummy_capability()],
        pagination=PaginationInfo(offset=0, limit=1, total_count=1),
    )


@router.get("/capabilities")
def get_all_capabilities(request_data: GetAllRequest = Depends()):
    return CapabilityMultipleResponse(
        capabilities=[create_dummy_capability()],
        pagination=PaginationInfo(offset=0, limit=1, total_count=1),
    )


@router.get("/roles/{app_name}/{namespace_name}/{name}/capabilities")
def get_capabilities_by_role(request_data: GetFullIdentifierRequest = Depends()):
    return CapabilityMultipleResponse(
        capabilities=[create_dummy_capability()],
        pagination=PaginationInfo(offset=0, limit=1, total_count=1),
    )


@router.post("/capabilities/{app_name}/{namespace_name}")
def create_capability_by_namespace(request_data: CapabilityCreateRequest = Depends()):
    return CapabilitySingleResponse(capability=create_dummy_capability())


@router.put("/capabilities/{app_name}/{namespace_name}/{name}")
def update_capability(request_data: CapabilityEditRequest = Depends()):
    return CapabilitySingleResponse(capability=create_dummy_capability())


@router.delete(
    "/capabilities/{app_name}/{namespace_name}/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_capability(request_data: GetFullIdentifierRequest = Depends()):
    return None
