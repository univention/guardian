# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
from .models.routers.app import (
    AppCreateRequest,
    AppEditRequest,
    AppGetRequest,
    AppMultipleResponse,
    AppsGetRequest,
    AppSingleResponse,
)
from .ports.app import AppAPIPort, AppPersistencePort
from .ports.condition import (
    APICreateRequestObject,
    APIEditRequestObject,
    APIGetMultipleRequestObject,
    APIGetMultipleResponseObject,
    APIGetSingleRequestObject,
    APIGetSingleResponseObject,
    ConditionAPIPort,
    ConditionPersistencePort,
)


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
) -> AppSingleResponse:
    try:
        query = await app_api_port.to_app_get(api_request)
        app = await persistence_port.read_one(query)
        return await app_api_port.to_api_get_response(app)
    except Exception as exc:
        raise (await app_api_port.transform_exception(exc)) from exc


async def get_apps(
    api_request: AppsGetRequest,
    app_api_port: AppAPIPort,
    persistence_port: AppPersistencePort,
) -> AppMultipleResponse:
    query = await app_api_port.to_apps_get(api_request)
    many_apps = await persistence_port.read_many(query)
    return await app_api_port.to_api_apps_get_response(
        apps=list(many_apps.objects),
        query_offset=query.pagination.query_offset,
        query_limit=query.pagination.query_limit
        if query.pagination.query_limit
        else many_apps.total_count,
        total_count=many_apps.total_count,
    )


async def edit_app(
    api_request: AppEditRequest,
    app_api_port: AppAPIPort,
    persistence_port: AppPersistencePort,
) -> AppSingleResponse:
    try:
        query = await app_api_port.to_app_edit(api_request)
        app = query.apps[0]
        updated_app = await persistence_port.update(app)
        return await app_api_port.to_api_edit_response(updated_app)
    except Exception as exc:
        raise (await app_api_port.transform_exception(exc)) from exc


async def get_condition(
    api_request: APIGetSingleRequestObject,
    api_port: ConditionAPIPort,
    persistence_port: ConditionPersistencePort,
) -> APIGetSingleResponseObject:
    try:
        query = await api_port.to_obj_get_single(api_request)
        condition = await persistence_port.read_one(query)
        return await api_port.to_api_get_single_response(condition)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def get_conditions(
    api_request: APIGetMultipleRequestObject,
    api_port: ConditionAPIPort,
    persistence_port: ConditionPersistencePort,
) -> APIGetMultipleResponseObject:
    try:
        query = await api_port.to_obj_get_multiple(api_request)
        many_conditions = await persistence_port.read_many(query)
        return await api_port.to_api_get_multiple_response(
            list(many_conditions.objects),
            query.pagination.query_offset,
            query.pagination.query_limit,
            many_conditions.total_count,
        )
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def create_condition(
    api_request: APICreateRequestObject,
    api_port: ConditionAPIPort,
    persistence_port: ConditionPersistencePort,
):
    try:
        query = await api_port.to_obj_create(api_request)
        condition = await persistence_port.create(query)
        return await api_port.to_api_get_single_response(condition)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def update_condition(
    api_request: APIEditRequestObject,
    api_port: ConditionAPIPort,
    persistence_port: ConditionPersistencePort,
):
    try:
        query, changed_values = await api_port.to_obj_edit(api_request)
        old_condition = await persistence_port.read_one(query)
        for key, value in changed_values.items():
            setattr(old_condition, key, value)
        condition = await persistence_port.update(old_condition)
        return await api_port.to_api_get_single_response(condition)

    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc
