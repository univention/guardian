# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict

from loguru import logger

from .adapters.namespace import FastAPINamespaceAPIAdapter
from .errors import UnauthorizedError
from .models.authz import Actor, OperationType, Resource, ResourceType
from .models.capability import (
    Capability,
    CapabilityConditionParameter,
    CapabilityConditionRelation,
    ParametrizedCondition,
)
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
from .models.routers.base import GetByAppRequest
from .models.routers.context import (
    ContextCreateRequest,
    ContextEditRequest,
    ContextGetRequest,
    ContextMultipleResponse,
    ContextSingleResponse,
)
from .models.routers.namespace import (
    NamespaceCreateRequest,
    NamespaceEditRequest,
    NamespaceGetRequest,
    NamespaceMultipleResponse,
    NamespacesGetRequest,
    NamespaceSingleResponse,
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
from .ports.app import (
    AppAPICreateRequestObject,
    AppAPIPort,
    AppAPIRegisterResponseObject,
    AppPersistencePort,
)
from .ports.authz import ResourceAuthorizationPort
from .ports.bundle_server import BundleServerPort, BundleType
from .ports.capability import CapabilityAPIPort, CapabilityPersistencePort
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
from .ports.context import (
    ContextAPIPort,
    ContextPersistencePort,
    ContextsAPIGetRequestObject,
)
from .ports.namespace import (
    NamespacePersistencePort,
)
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
    authz_port: ResourceAuthorizationPort,
) -> AppSingleResponse:
    try:
        query = await app_api_port.to_app_create(api_request)
        app = query.apps[0]
        allowed = (
            await authz_port.authorize_operation(
                Actor(id="test"),
                OperationType.CREATE_RESOURCE,
                [Resource(resource_type=ResourceType.APP, name=app.name)],
            )
        ).get(app.name, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to create this app."
            )
        created_app = await persistence_port.create(app)
        return await app_api_port.to_api_create_response(created_app)
    except Exception as exc:
        raise (await app_api_port.transform_exception(exc)) from exc


async def get_app(
    api_request: AppGetRequest,
    app_api_port: AppAPIPort,
    persistence_port: AppPersistencePort,
    authz_port: ResourceAuthorizationPort,
) -> AppSingleResponse:
    try:
        query = await app_api_port.to_app_get(api_request)
        app = await persistence_port.read_one(query)
        allowed = (
            await authz_port.authorize_operation(
                Actor(id="test"),
                OperationType.READ_RESOURCE,
                [Resource(resource_type=ResourceType.APP, name=app.name)],
            )
        ).get(app.name, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to read this app."
            )
        return await app_api_port.to_api_get_response(app)
    except Exception as exc:
        raise (await app_api_port.transform_exception(exc)) from exc


async def get_apps(
    api_request: AppsGetRequest,
    app_api_port: AppAPIPort,
    persistence_port: AppPersistencePort,
    authz_port: ResourceAuthorizationPort,
) -> AppMultipleResponse:
    try:
        query = await app_api_port.to_apps_get(api_request)
        many_apps = await persistence_port.read_many(query)
        authz_result = await authz_port.authorize_operation(
            Actor(id="test"),
            OperationType.READ_RESOURCE,
            [
                Resource(resource_type=ResourceType.APP, name=app.name)
                for app in many_apps.objects
            ],
        )
        allowed_apps = {
            resource_id
            for resource_id in authz_result.keys()
            if authz_result[resource_id]
        }
        return await app_api_port.to_api_apps_get_response(
            apps=[app for app in many_apps.objects if app.name in allowed_apps],
            query_offset=query.pagination.query_offset,
            query_limit=query.pagination.query_limit
            if query.pagination.query_limit
            else many_apps.total_count,
            total_count=many_apps.total_count,
        )
    except Exception as exc:
        raise (await app_api_port.transform_exception(exc)) from exc


async def create_namespace(
    api_request: NamespaceCreateRequest,
    namespace_api_port: FastAPINamespaceAPIAdapter,
    namespace_persistence_port: NamespacePersistencePort,
) -> NamespaceSingleResponse:
    query = await namespace_api_port.to_namespace_create(api_request)
    try:
        created_namespace = await namespace_persistence_port.create(query)
        logger.bind(query=query, created_namespace=created_namespace).debug(
            "Created Namespace."
        )
    except Exception as exc:
        raise (await namespace_api_port.transform_exception(exc)) from exc
    return await namespace_api_port.to_api_create_response(created_namespace)


async def edit_namespace(
    api_request: NamespaceEditRequest,
    namespace_api_port: FastAPINamespaceAPIAdapter,
    namespace_persistence_port: NamespacePersistencePort,
):
    query = await namespace_api_port.to_namespace_edit(api_request)
    try:
        updated_namespace = await namespace_persistence_port.update(query)
        logger.bind(query=query, updated_namespace=updated_namespace).debug(
            "Updated Namespace."
        )
    except Exception as exc:
        raise (await namespace_api_port.transform_exception(exc)) from exc
    return await namespace_api_port.to_api_edit_response(updated_namespace)


async def get_namespace(
    api_request: NamespaceGetRequest,
    namespace_api_port: FastAPINamespaceAPIAdapter,
    namespace_persistence_port: NamespacePersistencePort,
):
    query = await namespace_api_port.to_namespace_get(api_request)
    try:
        namespace = await namespace_persistence_port.read_one(query)
        logger.bind(query=query, namespace=namespace).debug("Retrieved Namespace.")
    except Exception as exc:
        raise (await namespace_api_port.transform_exception(exc)) from exc
    return await namespace_api_port.to_api_get_response(namespace)


async def get_namespaces(
    api_request: NamespacesGetRequest,
    namespace_api_port: FastAPINamespaceAPIAdapter,
    namespace_persistence_port: NamespacePersistencePort,
) -> NamespaceMultipleResponse:
    query = await namespace_api_port.to_namespaces_get(api_request)
    try:
        result = await namespace_persistence_port.read_many(query)
        logger.bind(query=query, namespaces=result).debug("Retrieved Namespaces.")
    except Exception as exc:
        raise (await namespace_api_port.transform_exception(exc)) from exc
    return await namespace_api_port.to_api_namespaces_get_response(
        namespaces=list(result.objects),
        query_offset=query.pagination.query_offset,
        query_limit=query.pagination.query_limit
        if query.pagination.query_limit
        else result.total_count,
        total_count=result.total_count,
    )


async def register_app(
    api_request: AppAPICreateRequestObject,
    app_api_port: AppAPIPort,
    app_persistence_port: AppPersistencePort,
    namespace_persistence_port: NamespacePersistencePort,
    role_persistence_port: RolePersistencePort,
    cap_persistence_port: CapabilityPersistencePort,
    bundle_server_port: BundleServerPort,
    authz_port: ResourceAuthorizationPort,
) -> AppAPIRegisterResponseObject:
    try:
        query = await app_api_port.to_app_create(api_request)
        allowed = (
            await authz_port.authorize_operation(
                Actor(id="test"),
                OperationType.CREATE_RESOURCE,
                [Resource(resource_type=ResourceType.APP, name=query.apps[0].name)],
            )
        ).get(query.apps[0].name, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to register this app."
            )
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
        await cap_persistence_port.create(
            Capability(
                app_name="guardian",
                namespace_name="management-api",
                name=f"{app.name}-admin-cap",
                display_name="App admin capability",
                role=admin_role,
                permissions=[
                    Permission(
                        app_name="guardian", namespace_name="management-api", name=name
                    )
                    for name in (
                        "create_resource",
                        "read_resource",
                        "update_resource",
                        "delete_resource",
                    )
                ],
                relation=CapabilityConditionRelation.AND,
                conditions=[
                    ParametrizedCondition(
                        app_name="guardian",
                        namespace_name="builtin",
                        name="target_field_equals_value",
                        parameters=[
                            CapabilityConditionParameter(name=name, value=value)
                            for name, value in [
                                ("field", "app_name"),
                                ("value", app.name),
                            ]
                        ],
                    )
                ],
            )
        )
        await cap_persistence_port.create(
            Capability(
                app_name="guardian",
                namespace_name="management-api",
                name=f"{app.name}-admin-cap-read-role-cond",
                display_name="App admin capability for read access to all roles and conditions",
                role=admin_role,
                permissions=[
                    Permission(
                        app_name="guardian",
                        namespace_name="management-api",
                        name="read_resource",
                    )
                ],
                relation=CapabilityConditionRelation.OR,
                conditions=[
                    ParametrizedCondition(
                        app_name="guardian",
                        namespace_name="builtin",
                        name="target_field_equals_value",
                        parameters=[
                            CapabilityConditionParameter(name=name, value=value)
                            for name, value in [
                                ("field", "resource_type"),
                                ("value", resource_type),
                            ]
                        ],
                    )
                    for resource_type in ("condition", "role")
                ],
            )
        )
        await bundle_server_port.schedule_bundle_build(BundleType.data)
        return await app_api_port.to_api_register_response(
            app, default_namespace, admin_role
        )
    except Exception as exc:
        logger.exception(exc)
        raise (await app_api_port.transform_exception(exc)) from exc


async def edit_app(
    api_request: AppEditRequest,
    app_api_port: AppAPIPort,
    persistence_port: AppPersistencePort,
    authz_port: ResourceAuthorizationPort,
) -> AppSingleResponse:
    try:
        query, changed_data = await app_api_port.to_app_edit(api_request)
        old_app = await persistence_port.read_one(query)
        allowed = (
            await authz_port.authorize_operation(
                Actor(id="test"),
                OperationType.UPDATE_RESOURCE,
                [Resource(resource_type=ResourceType.APP, name=old_app.name)],
            )
        ).get(old_app.name, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to edit this app."
            )
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
    bundle_server_port: BundleServerPort,
    persistence_port: ConditionPersistencePort,
):
    try:
        query = await api_port.to_obj_create(api_request)
        condition = await persistence_port.create(query)
        await bundle_server_port.schedule_bundle_build(BundleType.policies)
        return await api_port.to_api_get_single_response(condition)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def update_condition(
    api_request: APIEditRequestObject,
    api_port: ConditionAPIPort,
    bundle_server_port: BundleServerPort,
    persistence_port: ConditionPersistencePort,
):
    try:
        query, changed_values = await api_port.to_obj_edit(api_request)
        old_condition = await persistence_port.read_one(query)
        for key, value in changed_values.items():
            setattr(old_condition, key, value)
        condition = await persistence_port.update(old_condition)
        await bundle_server_port.schedule_bundle_build(BundleType.policies)
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
    try:
        query = await role_api_port.to_role_create(api_request)
        role = query.roles[0]
        created_role = await persistence_port.create(role)
        return await role_api_port.to_role_create_response(created_role)
    except Exception as exc:
        raise (await role_api_port.transform_exception(exc)) from exc


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
        created_context = await persistence_port.create(query)
        logger.bind(query=query, created_context=created_context).debug(
            "Context created."
        )
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc
    return await api_port.to_api_create_response(created_context)


async def get_context(
    api_request: ContextGetRequest,
    api_port: ContextAPIPort,
    persistence_port: ContextPersistencePort,
) -> ContextSingleResponse:
    try:
        query = await api_port.to_context_get(api_request)
        context = await persistence_port.read_one(query)
        logger.bind(query=query, context=context).debug("Retrieved context.")
        return await api_port.to_api_get_response(context)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def get_contexts(
    api_request: ContextsAPIGetRequestObject,
    api_port: ContextAPIPort,
    persistence_port: ContextPersistencePort,
) -> ContextMultipleResponse:
    try:
        query = await api_port.to_contexts_get(api_request)
        contexts = await persistence_port.read_many(query)
        logger.bind(query=query, contexts=contexts).debug("Retrieved contexts.")
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
        logger.bind(query=query, updated_context=updated_context).debug(
            "Updated context."
        )
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc
    return await api_port.to_api_edit_response(updated_context)


async def get_namespaces_by_app(
    api_request: GetByAppRequest,
    namespace_api_port: FastAPINamespaceAPIAdapter,
    namespace_persistence_port: NamespacePersistencePort,
):
    query = await namespace_api_port.to_namespaces_by_appname_get(api_request)
    try:
        result = await namespace_persistence_port.read_many(query)
        logger.bind(query=query, namespaces=result).debug("Retrieved Namespaces.")
    except Exception as exc:
        raise (
            await namespace_api_port.transform_exception(exc)
        ) from exc  # pragma: no cover
    return await namespace_api_port.to_api_namespaces_get_response(
        namespaces=list(result.objects),
        query_offset=query.pagination.query_offset,
        query_limit=query.pagination.query_limit
        if query.pagination.query_limit
        else result.total_count,
        total_count=result.total_count,
    )


async def get_capability(
    api_request: APIGetSingleRequestObject,
    api_port: CapabilityAPIPort,
    persistence_port: CapabilityPersistencePort,
):
    try:
        query = await api_port.to_obj_get_single(api_request)
        capability = await persistence_port.read_one(query)
        return await api_port.to_api_get_single_response(capability)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def get_capabilities(
    api_request: APIGetMultipleRequestObject,
    api_port: CapabilityAPIPort,
    persistence_port: CapabilityPersistencePort,
) -> APIGetMultipleResponseObject:
    try:
        query = await api_port.to_obj_get_multiple(api_request)
        many_capabilities = await persistence_port.read_many(query)
        return await api_port.to_api_get_multiple_response(
            list(many_capabilities.objects),
            query.pagination.query_offset,
            query.pagination.query_limit,
            many_capabilities.total_count,
        )
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def create_capability(
    api_request: APICreateRequestObject,
    api_port: CapabilityAPIPort,
    bundle_server_port: BundleServerPort,
    persistence_port: CapabilityPersistencePort,
):
    try:
        query = await api_port.to_obj_create(api_request)
        capability = await persistence_port.create(query)
        await bundle_server_port.schedule_bundle_build(BundleType.data)
        return await api_port.to_api_get_single_response(capability)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def update_capability(
    api_request: APIEditRequestObject,
    api_port: CapabilityAPIPort,
    bundle_server_port: BundleServerPort,
    persistence_port: CapabilityPersistencePort,
):
    try:
        edited_capability = await api_port.to_obj_edit(api_request)
        capability = await persistence_port.update(edited_capability)
        await bundle_server_port.schedule_bundle_build(BundleType.data)
        return await api_port.to_api_get_single_response(capability)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def delete_capability(
    api_request: APIEditRequestObject,
    api_port: CapabilityAPIPort,
    bundle_server_port: BundleServerPort,
    persistence_port: CapabilityPersistencePort,
):
    try:
        query = await api_port.to_obj_get_single(api_request)
        await persistence_port.delete(query)
        await bundle_server_port.schedule_bundle_build(BundleType.data)
        return None
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc
