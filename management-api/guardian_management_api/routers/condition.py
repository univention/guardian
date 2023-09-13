# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from fastapi import APIRouter, Depends
from guardian_lib.adapter_registry import port_dep

from .. import business_logic
from ..adapters.condition import FastAPIConditionAPIAdapter
from ..models.routers.base import (
    GetAllRequest,
    GetByAppRequest,
    GetByNamespaceRequest,
    GetFullIdentifierRequest,
)
from ..models.routers.condition import (
    ConditionCreateRequest,
    ConditionEditRequest,
    ConditionMultipleResponse,
    ConditionSingleResponse,
)
from ..ports.bundle_server import BundleServerPort
from ..ports.condition import ConditionAPIPort, ConditionPersistencePort

router = APIRouter(tags=["condition"])


@router.get(
    "/conditions/{app_name}/{namespace_name}/{name}",
    response_model=ConditionSingleResponse,
)
async def get_condition(
    condition_get_request: GetFullIdentifierRequest = Depends(),
    api_port: FastAPIConditionAPIAdapter = Depends(
        port_dep(ConditionAPIPort, FastAPIConditionAPIAdapter)
    ),
    persistence_port: ConditionPersistencePort = Depends(
        port_dep(ConditionPersistencePort)
    ),
):
    """
    Returns a condition object identified by `app_name`, `namespace_name` and `name`.
    """
    return await business_logic.get_condition(
        condition_get_request, api_port, persistence_port
    )


@router.get("/conditions", response_model=ConditionMultipleResponse)
async def get_all_conditions(
    condition_get_request: GetAllRequest = Depends(),
    api_port: FastAPIConditionAPIAdapter = Depends(
        port_dep(ConditionAPIPort, FastAPIConditionAPIAdapter)
    ),
    persistence_port: ConditionPersistencePort = Depends(
        port_dep(ConditionPersistencePort)
    ),
):
    """
    Returns a list of all conditions.
    """
    return await business_logic.get_conditions(
        condition_get_request, api_port, persistence_port
    )


@router.get("/conditions/{app_name}", response_model=ConditionMultipleResponse)
async def get_conditions_by_app(
    condition_get_request: GetByAppRequest = Depends(),
    api_port: FastAPIConditionAPIAdapter = Depends(
        port_dep(ConditionAPIPort, FastAPIConditionAPIAdapter)
    ),
    persistence_port: ConditionPersistencePort = Depends(
        port_dep(ConditionPersistencePort)
    ),
):
    """
    Returns a list of all conditions that belong to `app_name`.
    """
    return await business_logic.get_conditions(
        condition_get_request, api_port, persistence_port
    )


@router.get(
    "/conditions/{app_name}/{namespace_name}", response_model=ConditionMultipleResponse
)
async def get_conditions_by_namespace(
    condition_get_request: GetByNamespaceRequest = Depends(),
    api_port: FastAPIConditionAPIAdapter = Depends(
        port_dep(ConditionAPIPort, FastAPIConditionAPIAdapter)
    ),
    persistence_port: ConditionPersistencePort = Depends(
        port_dep(ConditionPersistencePort)
    ),
):
    """
    Returns a list of all conditions that belong to `namespace_name` under `app_name`.
    """
    return await business_logic.get_conditions(
        condition_get_request, api_port, persistence_port
    )


@router.post(
    "/conditions/{app_name}/{namespace_name}",
    response_model=ConditionSingleResponse,
    status_code=201,
)
async def create_condition(
    condition_create_request: ConditionCreateRequest = Depends(),
    api_port: FastAPIConditionAPIAdapter = Depends(
        port_dep(ConditionAPIPort, FastAPIConditionAPIAdapter)
    ),
    persistence_port: ConditionPersistencePort = Depends(
        port_dep(ConditionPersistencePort)
    ),
    bundle_server_port: BundleServerPort = Depends(port_dep(BundleServerPort)),
):
    """
    Create a condition.
    """
    return await business_logic.create_condition(
        condition_create_request, api_port, bundle_server_port, persistence_port
    )


@router.patch(
    "/conditions/{app_name}/{namespace_name}/{name}",
    response_model=ConditionSingleResponse,
)
async def edit_condition(
    condition_edit_request: ConditionEditRequest = Depends(),
    api_port: FastAPIConditionAPIAdapter = Depends(
        port_dep(ConditionAPIPort, FastAPIConditionAPIAdapter)
    ),
    persistence_port: ConditionPersistencePort = Depends(
        port_dep(ConditionPersistencePort)
    ),
    bundle_server_port: BundleServerPort = Depends(port_dep(BundleServerPort)),
):
    """
    Update a condition.
    """
    return await business_logic.update_condition(
        condition_edit_request, api_port, bundle_server_port, persistence_port
    )
