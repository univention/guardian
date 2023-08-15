# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from .models.routers.app import (
    ManagementAppCreateRequest,
    ManagementAppCreateResponse,
    ManagementAppGetRequest,
    ManagementAppGetResponse,
)
from .ports.app import AppAPIPort, AppPersistencePort


async def create_app(
    api_request: ManagementAppCreateRequest,
    management_app_api_port: AppAPIPort,
    persistence_port: AppPersistencePort,
) -> ManagementAppCreateResponse:
    query = await management_app_api_port.to_app_create(api_request)
    app = query.apps[0]
    created_app = await persistence_port.create(app)
    return await management_app_api_port.to_api_create_response(created_app)


async def get_app(
    api_request: ManagementAppGetRequest,
    management_app_api_port: AppAPIPort,
    persistence_port: AppPersistencePort,
) -> ManagementAppGetResponse | None:
    query = await management_app_api_port.to_app_get(api_request)
    app = await persistence_port.read_one(query)
    return await management_app_api_port.to_api_get_response(app)
