# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from .models.routers.app import (
    AppCreateRequest,
    AppGetRequest,
    AppMultipleResponse,
    AppsGetRequest,
    AppSingleResponse,
)
from .ports.app import AppAPIPort, AppPersistencePort


async def create_app(
    api_request: AppCreateRequest,
    app_api_port: AppAPIPort,
    persistence_port: AppPersistencePort,
) -> AppSingleResponse:
    query = await app_api_port.to_app_create(api_request)
    app = query.apps[0]
    created_app = await persistence_port.create(app)
    return await app_api_port.to_api_create_response(created_app)


async def get_app(
    api_request: AppGetRequest,
    app_api_port: AppAPIPort,
    persistence_port: AppPersistencePort,
) -> AppSingleResponse | None:
    query = await app_api_port.to_app_get(api_request)
    app = await persistence_port.read_one(query)
    return await app_api_port.to_api_get_response(app)


async def get_apps(
    api_request: AppsGetRequest,
    app_api_port: AppAPIPort,
    persistence_port: AppPersistencePort,
) -> AppMultipleResponse:
    query = await app_api_port.to_apps_get(api_request)
    many_apps = await persistence_port.read_many(query)
    return await app_api_port.to_api_apps_get_response(
        apps=many_apps.apps,
        query_offset=query.pagination.query_offset,
        query_limit=query.pagination.query_limit
        if query.pagination.query_limit
        else many_apps.total_count,
        total_count=many_apps.total_count,
    )