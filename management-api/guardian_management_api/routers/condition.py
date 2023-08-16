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
from ..models.routers.condition import (
    Condition as ResponseCondition,
)
from ..models.routers.condition import (
    ConditionCreateRequest,
    ConditionEditRequest,
    ConditionMultipleResponse,
    ConditionSingleResponse,
)

router = APIRouter(tags=["condition"])


@router.get(
    "/conditions/{app_name}/{namespace_name}/{name}",
    response_model=ConditionSingleResponse,
)
async def get_condition(condition_get_request: GetFullIdentifierRequest = Depends()):
    """
    Returns a condition object identified by `app_name`, `namespace_name` and `name`.
    """
    return ConditionSingleResponse(
        condition=ResponseCondition(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-condition",
            display_name="My Condition",
            resource_url="http://fqdn/guardian/management/conditions/my-app/my-namespace/my-condition",
            documentation="Some dummy condition.",
            parameter_names=["A", "B", "C"],
        )
    ).dict()


@router.get("/conditions", response_model=ConditionMultipleResponse)
async def get_all_conditions(condition_get_request: GetAllRequest = Depends()):
    """
    Returns a list of all conditions.
    """
    return ConditionMultipleResponse(
        conditions=[
            ResponseCondition(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-condition",
                display_name="My Condition",
                resource_url="http://fqdn/guardian/management/conditions/my-app/my-namespace/my-condition",
                documentation="Some dummy condition.",
                parameter_names=["A", "B", "C"],
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.get("/conditions/{app_name}", response_model=ConditionMultipleResponse)
async def get_conditions_by_app(condition_get_request: GetByAppRequest = Depends()):
    """
    Returns a list of all conditions that belong to `app_name`.
    """
    return ConditionMultipleResponse(
        conditions=[
            ResponseCondition(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-condition",
                display_name="My Condition",
                resource_url="http://fqdn/guardian/management/conditions/my-app/my-namespace/my-condition",
                documentation="Some dummy condition.",
                parameter_names=["A", "B", "C"],
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.get(
    "/conditions/{app_name}/{namespace_name}", response_model=ConditionMultipleResponse
)
async def get_conditions_by_namespace(
    condition_get_request: GetByNamespaceRequest = Depends(),
):
    """
    Returns a list of all conditions that belong to `namespace_name` under `app_name`.
    """
    return ConditionMultipleResponse(
        conditions=[
            ResponseCondition(
                app_name="my-app",
                namespace_name="my-namespace",
                name="my-condition",
                display_name="My Condition",
                resource_url="http://fqdn/guardian/management/conditions/my-app/my-namespace/my-condition",
                documentation="Some dummy condition.",
                parameter_names=["A", "B", "C"],
            )
        ],
        pagination=PaginationInfo(limit=1000, offset=0, total_count=1),
    ).dict()


@router.post(
    "/conditions/{app_name}/{namespace_name}", response_model=ConditionSingleResponse
)
async def create_condition(
    condition_create_request: ConditionCreateRequest = Depends(),
):
    """
    Create a condition.
    """
    return ConditionSingleResponse(
        condition=ResponseCondition(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-condition",
            display_name="My Condition",
            resource_url="http://fqdn/guardian/management/conditions/my-app/my-namespace/my-condition",
            documentation="Some dummy condition.",
            parameter_names=["A", "B", "C"],
        )
    ).dict()


@router.patch(
    "/conditions/{app_name}/{namespace_name}/{name}",
    response_model=ConditionSingleResponse,
)
async def edit_condition(condition_edit_request: ConditionEditRequest = Depends()):
    """
    Update a condition.
    """
    return ConditionSingleResponse(
        condition=ResponseCondition(
            app_name="my-app",
            namespace_name="my-namespace",
            name="my-condition",
            display_name="My Condition",
            resource_url="http://fqdn/guardian/management/conditions/my-app/my-namespace/my-condition",
            documentation="Some dummy condition.",
            parameter_names=["A", "B", "C"],
        )
    ).dict()
