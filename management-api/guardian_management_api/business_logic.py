# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict

from .models.namespace import Namespace
from .models.permission import Permission
from .models.role import Role
from .models.routers.app import (
    AppCreateRequest,
    AppEditRequest,
    AppGetRequest,
    AppMultipleResponse,
    AppsGetRequest,
    AppSingleResponse,
)
from .models.routers.role import (
    RoleCreateRequest,
    RoleEditRequest,
    RoleGetAllRequest,
    RoleGetByAppRequest,
    RoleGetByNamespaceRequest,
    RoleGetFullIdentifierRequest,
    RoleMultipleResponse,
    RoleSingleResponse,
)
from .models.routers.context import ContextCreateRequest
from .models.routers.context import (
    ContextCreateRequest,
    ContextEditRequest,
    ContextGetRequest,
    ContextMultipleResponse,
    ContextsGetRequest,
    ContextSingleResponse,
)
from .ports.app import (
    AppAPICreateRequestObject,
    AppAPIPort,
    AppAPIRegisterResponseObject,
    AppPersistencePort,
)
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
from .ports.context import ContextAPIPort, ContextPersistencePort
from .ports.namespace import NamespacePersistencePort
from .ports.permission import (
    PermissionAPICreateRequestObject,
    PermissionAPIEditRequestObject,
    PermissionAPIGetMultipleRequestObject,
    PermissionAPIGetMultipleResponseObject,
    PermissionAPIGetSingleRequestObject,
    PermissionAPIGetSingleResponseObject,
    PermissionAPIPort,
    PermissionPersistencePort,
)
from .ports.role import RoleAPIPort, RolePersistencePort


async def create_app(
    api_request: AppCreateRequest,
    app_api_port: AppAPIPort,
    persistence_port: AppPersistencePort,
) -> AppSingleResponse:
    query = await app_api_port.to_app_create(api_request)
    app = query.apps[0]
    created_app = await persistence_port.create(app)
    return await app_api_port.to_api_create_response(created_app)


async def register_app(
    api_request: AppAPICreateRequestObject,
    app_api_port: AppAPIPort,
    app_persistence_port: AppPersistencePort,
    namespace_persistence_port: NamespacePersistencePort,
    role_persistence_port: RolePersistencePort,
) -> AppAPIRegisterResponseObject:
    try:
        query = await app_api_port.to_app_create(api_request)
        app = await app_persistence_port.create(query.apps[0])
        app_display = app.display_name if app.display_name else app.name
        default_namespace = await namespace_persistence_port.create(
            Namespace(
                app_name=app.name,
                name="default",
                display_name=f"Default Namespace for {app_display}",
            )
        )
        admin_role = await role_persistence_port.create(
            Role(
                app_name=app.name,
                namespace_name=default_namespace.name,
                name="app-admin",
                display_name=f"App Administrator for {app_display}",
            )
        )
        return await app_api_port.to_api_register_response(
            app, default_namespace, admin_role
        )
    except Exception as exc:
        raise (await app_api_port.transform_exception(exc)) from exc


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
        query, changed_data = await app_api_port.to_app_edit(api_request)
        old_app = await persistence_port.read_one(query)
        for key, value in changed_data.items():
            setattr(old_app, key, value)
        updated_app = await persistence_port.update(old_app)
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


async def create_permission(
    api_request: PermissionAPICreateRequestObject,
    api_port: PermissionAPIPort,
    persistence_port: PermissionPersistencePort,
) -> PermissionAPIGetSingleResponseObject:
    try:
        query = await api_port.to_obj_create(api_request)
        permission = query.permissions[0]
        created_permission = await persistence_port.create(permission)
        return await api_port.to_api_get_single_response(created_permission)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def get_permission(
    api_request: PermissionAPIGetSingleRequestObject,
    api_port: PermissionAPIPort,
    persistence_port: PermissionPersistencePort,
) -> PermissionAPIGetSingleResponseObject:
    try:
        query = await api_port.to_obj_get_single(api_request)
        permission = await persistence_port.read_one(query)
        return await api_port.to_api_get_single_response(permission)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def get_permissions(
    api_request: PermissionAPIGetMultipleRequestObject,
    api_port: PermissionAPIPort,
    persistence_port: PermissionPersistencePort,
) -> PermissionAPIGetMultipleResponseObject:
    try:
        query = await api_port.to_obj_get_multiple(api_request)
        many_permissions = await persistence_port.read_many(query)
        return await api_port.to_api_get_multiple_response(
            objs=list(many_permissions.objects),
            query_offset=query.pagination.query_offset,
            query_limit=query.pagination.query_limit
            if query.pagination.query_limit
            else many_permissions.total_count,
            total_count=many_permissions.total_count,
        )
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def edit_permission(
    api_request: PermissionAPIEditRequestObject,
    api_port: PermissionAPIPort,
    persistence_port: PermissionPersistencePort,
) -> PermissionAPIGetSingleResponseObject:
    try:
        query, changed_values = await api_port.to_obj_edit(api_request)
        old_permission = await persistence_port.read_one(query)
        vals = asdict(old_permission)
        vals.update(changed_values)
        new_permission = Permission(**vals)
        update_permission = await persistence_port.update(new_permission)
        return await api_port.to_api_get_single_response(update_permission)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


##############
# Role Logic #
##############


async def get_role(
    api_request: RoleGetFullIdentifierRequest,
    role_api_port: RoleAPIPort,
    persistence_port: RolePersistencePort,
) -> RoleSingleResponse:
    try:
        query = await role_api_port.to_role_get(api_request)
        role = await persistence_port.read_one(query)
        return await role_api_port.to_role_get_response(role)
    except Exception as exc:
        raise (await role_api_port.transform_exception(exc)) from exc


async def get_roles(
    api_request: RoleGetAllRequest | RoleGetByAppRequest | RoleGetByNamespaceRequest,
    role_api_port: RoleAPIPort,
    persistence_port: RolePersistencePort,
) -> RoleMultipleResponse:
    try:
        query = await role_api_port.to_roles_get(api_request)
        many_roles = await persistence_port.read_many(query)
        return await role_api_port.to_roles_get_response(
            roles=list(many_roles.objects),
            query_offset=query.pagination.query_offset,
            query_limit=query.pagination.query_limit
            if query.pagination.query_limit
            else many_roles.total_count,
            total_count=many_roles.total_count,
        )
    except Exception as exc:
        raise (await role_api_port.transform_exception(exc)) from exc


async def create_role(
    api_request: RoleCreateRequest,
    role_api_port: RoleAPIPort,
    persistence_port: RolePersistencePort,
) -> RoleSingleResponse:
    query = await role_api_port.to_role_create(api_request)
    role = query.roles[0]
    created_role = await persistence_port.create(role)
    return await role_api_port.to_role_create_response(created_role)


async def edit_role(
    api_request: RoleEditRequest,
    role_api_port: RoleAPIPort,
    persistence_port: RolePersistencePort,
) -> RoleSingleResponse:
    try:
        query = await role_api_port.to_role_get(api_request)
        role = await persistence_port.read_one(query)
        role = await role_api_port.to_role_edit(
            old_role=role, display_name=api_request.data.display_name
        )
        modified_role = await persistence_port.update(role)
        return await role_api_port.to_role_get_response(modified_role)
    except Exception as exc:
        raise (await role_api_port.transform_exception(exc)) from exc


async def create_context(
    api_request: ContextCreateRequest,
    persistence_port: ContextPersistencePort,
    api_port: ContextAPIPort,
):
    query = await api_port.to_context_create(api_request)
    try:
        created_namespace = await persistence_port.create(query)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc
    return await api_port.to_api_create_response(created_namespace)


async def get_context(
    api_request: ContextGetRequest,
    api_port: ContextAPIPort,
    persistence_port: ContextPersistencePort,
) -> ContextSingleResponse:
    try:
        query = await api_port.to_context_get(api_request)
        condition = await persistence_port.read_one(query)
        return await api_port.to_api_get_response(condition)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def get_contexts(
    api_request: ContextsGetRequest,
    api_port: ContextAPIPort,
    persistence_port: ContextPersistencePort,
) -> ContextMultipleResponse:
    try:
        query = await api_port.to_contexts_get(api_request)
        contexts = await persistence_port.read_many(query)
        return await api_port.to_api_contexts_get_response(
            list(contexts.objects),
            query.pagination.query_offset,
            query.pagination.query_limit,
            contexts.total_count,
        )
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def edit_context(
    api_request: ContextEditRequest,
    api_port: ContextAPIPort,
    persistence_port: ContextPersistencePort,
):
    try:
        query, changed_values = await api_port.to_context_edit(api_request)
        obj = await persistence_port.read_one(query)
        for key, value in changed_values.items():
            setattr(obj, key, value)
        updated_context = await persistence_port.update(obj)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc
    return await api_port.to_api_edit_response(updated_context)
