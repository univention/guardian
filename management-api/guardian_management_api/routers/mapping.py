# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from fastapi import APIRouter, Depends

from ..models.routers.mapping import (
    Capability,
    MappingCondition,
    MappingPermission,
    MappingRole,
    RCMapping,
    RCMappingDeleteRequest,
    RCMappingGetAllRequest,
    RCMappingGetByNamespaceRequest,
    RCMappingResponse,
    RCMappingUpdateAllRequest,
    RCMappingUpdateByNamespaceRequest,
    RelationChoices,
)

router = APIRouter(tags=["role_capability_mapping"])

DUMMY_MAPPING = RCMapping(
    mappings=[
        Capability(
            role=MappingRole(
                app_name="my-app", namespace_name="my-namespace", name="my-role"
            ),
            conditions=[
                MappingCondition(
                    app_name="my-app",
                    namespace_name="my-namespace",
                    name="my-condition",
                    parameters={"A": 1, "B": False},
                )
            ],
            relation=RelationChoices.AND,
            permissions=[
                MappingPermission(
                    app_name="my-app",
                    namespace_name="my-namespace",
                    name="my-permission",
                )
            ],
        )
    ]
)


@router.get(
    "/role_capability_mappings/{app_name}/{namespace_name}",
    response_model=RCMappingResponse,
)
async def get_role_capability_mapping(
    role_capability_mapping_get_request: RCMappingGetByNamespaceRequest = Depends(),
):
    """
    Returns a view on the role_capability_mapping filtered by `app_name` and `namespace_name`.
    """
    return RCMappingResponse(role_capability_mapping=DUMMY_MAPPING).dict()


@router.get("/role_capability_mappings", response_model=RCMappingResponse)
async def get_all_role_capability_mappings(
    role_capability_mapping_get_request: RCMappingGetAllRequest = Depends(),
):
    """
    Returns the complete role_capability_mapping.
    """
    return RCMappingResponse(role_capability_mapping=DUMMY_MAPPING).dict()


@router.put(
    "/role_capability_mappings/{app_name}/{namespace_name}",
    response_model=RCMappingResponse,
)
async def update_role_capability_mapping_by_namespace(
    role_capability_mapping_create_request: RCMappingUpdateByNamespaceRequest = Depends(),
):
    """
    Update the role_capability_mapping in the context of a specific namespace.
    """
    return RCMappingResponse(role_capability_mapping=DUMMY_MAPPING).dict()


@router.put("/role_capability_mappings", response_model=RCMappingResponse)
async def update_role_capability_mapping_global(
    role_capability_mapping_create_request: RCMappingUpdateAllRequest = Depends(),
):
    """
    Update the complete role_capability_mapping.
    """
    return RCMappingResponse(role_capability_mapping=DUMMY_MAPPING).dict()


@router.delete(
    "/role_capability_mappings/{app_name}/{namespace_name}",
    response_model=RCMappingResponse,
)
async def delete_role_capability_mapping(
    role_capability_mapping_create_request: RCMappingDeleteRequest = Depends(),
):
    """
    Update a role_capability_mapping.
    """
    return RCMappingResponse(role_capability_mapping=DUMMY_MAPPING).dict()
