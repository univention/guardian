# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from .models.routes import (
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
    query = await management_app_api_port.create_to_query(api_request)
    app = query.apps[0]
    await persistence_port.create(app)
    return await management_app_api_port.create_to_api_response(app)


async def get_app(
    api_request: ManagementAppGetRequest,
    management_app_api_port: AppAPIPort,
    persistence_port: AppPersistencePort,
) -> ManagementAppGetResponse | None:
    query = await management_app_api_port.get_to_query(api_request)
    app = await persistence_port.read_one(query)
    return await management_app_api_port.get_to_api_response(app)
