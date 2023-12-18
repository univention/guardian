# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import asdict

from fastapi import Request
from guardian_lib.ports import AuthenticationPort
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> AppSingleResponse:
    try:
        query = await app_api_port.to_app_create(api_request)
        app = query.apps[0]
        actor_id: str = await authc_port.get_actor_identifier(request)
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> AppSingleResponse:
    try:
        query = await app_api_port.to_app_get(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource = Resource(resource_type=ResourceType.APP, name=query.name)
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id), OperationType.READ_RESOURCE, [resource]
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to read this app."
            )
        app = await persistence_port.read_one(query)
        return await app_api_port.to_api_get_response(app)
    except Exception as exc:
        raise (await app_api_port.transform_exception(exc)) from exc


async def get_apps(
    api_request: AppsGetRequest,
    app_api_port: AppAPIPort,
    persistence_port: AppPersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> AppMultipleResponse:
    try:
        query = await app_api_port.to_apps_get(api_request)
        many_apps = await persistence_port.read_many(query)
        actor_id: str = await authc_port.get_actor_identifier(request)
        authz_result = await authz_port.authorize_operation(
            Actor(id=actor_id),
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
            apps=[
                app
                for app in many_apps.objects
                if Resource(resource_type=ResourceType.APP, name=app.name).id
                in allowed_apps
            ],
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> NamespaceSingleResponse:
    try:
        query = await namespace_api_port.to_namespace_create(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.NAMESPACE,
            name=query.name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.CREATE_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to create this namespace."
            )
        created_namespace = await namespace_persistence_port.create(query)
        logger.bind(query=query, created_namespace=created_namespace).debug(
            "Created Namespace."
        )
        return await namespace_api_port.to_api_create_response(created_namespace)
    except Exception as exc:
        raise (await namespace_api_port.transform_exception(exc)) from exc


async def edit_namespace(
    api_request: NamespaceEditRequest,
    namespace_api_port: FastAPINamespaceAPIAdapter,
    namespace_persistence_port: NamespacePersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
):
    try:
        query = await namespace_api_port.to_namespace_edit(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.NAMESPACE,
            name=query.name,
            app_name=query.app_name,
            namespace_name=query.name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.UPDATE_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to update this namespace."
            )
        updated_namespace = await namespace_persistence_port.update(query)
        logger.bind(query=query, updated_namespace=updated_namespace).debug(
            "Updated Namespace."
        )
        return await namespace_api_port.to_api_edit_response(updated_namespace)
    except Exception as exc:
        raise (await namespace_api_port.transform_exception(exc)) from exc


async def get_namespace(
    api_request: NamespaceGetRequest,
    namespace_api_port: FastAPINamespaceAPIAdapter,
    namespace_persistence_port: NamespacePersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
):
    try:
        query = await namespace_api_port.to_namespace_get(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.NAMESPACE,
            name=query.name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.READ_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to read this namespace."
            )
        namespace = await namespace_persistence_port.read_one(query)
        logger.bind(query=query, namespace=namespace).debug("Retrieved Namespace.")
        return await namespace_api_port.to_api_get_response(namespace)
    except Exception as exc:
        raise (await namespace_api_port.transform_exception(exc)) from exc


async def get_namespaces(
    api_request: NamespacesGetRequest,
    namespace_api_port: FastAPINamespaceAPIAdapter,
    namespace_persistence_port: NamespacePersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> NamespaceMultipleResponse:
    try:
        query = await namespace_api_port.to_namespaces_get(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        namespaces_persistence = await namespace_persistence_port.read_many(query)
        logger.bind(query=query, namespaces=namespaces_persistence).debug(
            "Retrieved Namespaces."
        )
        authz_result = await authz_port.authorize_operation(
            Actor(id=actor_id),
            OperationType.READ_RESOURCE,
            [
                Resource(
                    resource_type=ResourceType.NAMESPACE,
                    name=namespace.name,
                    app_name=namespace.app_name,
                )
                for namespace in namespaces_persistence.objects
            ],
        )
        allowed_namespaces = {
            resource_id
            for resource_id in authz_result.keys()
            if authz_result[resource_id]
        }
        return await namespace_api_port.to_api_namespaces_get_response(
            namespaces=[
                ns
                for ns in namespaces_persistence.objects
                if Resource(
                    resource_type=ResourceType.NAMESPACE,
                    name=ns.name,
                    app_name=ns.app_name,
                ).id
                in allowed_namespaces
            ],
            query_offset=query.pagination.query_offset,
            query_limit=query.pagination.query_limit
            if query.pagination.query_limit
            else namespaces_persistence.total_count,
            total_count=namespaces_persistence.total_count,
        )
    except Exception as exc:
        raise (await namespace_api_port.transform_exception(exc)) from exc


async def register_app(
    api_request: AppAPICreateRequestObject,
    app_api_port: AppAPIPort,
    app_persistence_port: AppPersistencePort,
    namespace_persistence_port: NamespacePersistencePort,
    role_persistence_port: RolePersistencePort,
    cap_persistence_port: CapabilityPersistencePort,
    bundle_server_port: BundleServerPort,
    authz_port: ResourceAuthorizationPort,
    authc_port: AuthenticationPort,
    request: Request,
) -> AppAPIRegisterResponseObject:
    try:
        query = await app_api_port.to_app_create(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource = Resource(resource_type=ResourceType.APP, name=query.apps[0].name)
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id), OperationType.CREATE_RESOURCE, [resource]
            )
        ).get(resource.id, False)
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> AppSingleResponse:
    try:
        query, changed_data = await app_api_port.to_app_edit(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource = Resource(resource_type=ResourceType.APP, name=query.name)
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.UPDATE_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to edit this app."
            )
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> APIGetSingleResponseObject:
    try:
        query = await api_port.to_obj_get_single(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.CONDITION,
            name=query.name,
            namespace_name=query.namespace_name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.READ_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to read this condition."
            )
        condition = await persistence_port.read_one(query)
        return await api_port.to_api_get_single_response(condition)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def get_conditions(
    api_request: APIGetMultipleRequestObject,
    api_port: ConditionAPIPort,
    persistence_port: ConditionPersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> APIGetMultipleResponseObject:
    try:
        query = await api_port.to_obj_get_multiple(api_request)
        many_conditions = await persistence_port.read_many(query)
        actor_id: str = await authc_port.get_actor_identifier(request)
        authz_result = await authz_port.authorize_operation(
            Actor(id=actor_id),
            OperationType.READ_RESOURCE,
            [
                Resource(
                    resource_type=ResourceType.CONDITION,
                    name=condition.name,
                    namespace_name=condition.namespace_name,
                    app_name=condition.app_name,
                )
                for condition in many_conditions.objects
            ],
        )
        allowed_conditions = {
            resource_id
            for resource_id in authz_result.keys()
            if authz_result[resource_id]
        }
        return await api_port.to_api_get_multiple_response(
            [
                condition
                for condition in many_conditions.objects
                if Resource(
                    resource_type=ResourceType.CONDITION,
                    name=condition.name,
                    namespace_name=condition.namespace_name,
                    app_name=condition.app_name,
                ).id
                in allowed_conditions
            ],
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
):
    try:
        query = await api_port.to_obj_create(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.CONDITION,
            name=query.name,
            namespace_name=query.namespace_name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.CREATE_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to create this condition."
            )
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
):
    try:
        query, changed_values = await api_port.to_obj_edit(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.CONDITION,
            name=query.name,
            namespace_name=query.namespace_name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.UPDATE_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to update this condition."
            )
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> PermissionAPIGetSingleResponseObject:
    try:
        query = await api_port.to_obj_create(api_request)
        permission = query.permissions[0]
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.PERMISSION,
            name=permission.name,
            namespace_name=permission.namespace_name,
            app_name=permission.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.CREATE_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to create this permission."
            )
        created_permission = await persistence_port.create(permission)
        return await api_port.to_api_get_single_response(created_permission)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def get_permission(
    api_request: PermissionAPIGetSingleRequestObject,
    api_port: PermissionAPIPort,
    persistence_port: PermissionPersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> PermissionAPIGetSingleResponseObject:
    try:
        query = await api_port.to_obj_get_single(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.PERMISSION,
            name=query.name,
            namespace_name=query.namespace_name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.READ_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to read this permission."
            )
        permission = await persistence_port.read_one(query)
        return await api_port.to_api_get_single_response(permission)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def get_permissions(
    api_request: PermissionAPIGetMultipleRequestObject,
    api_port: PermissionAPIPort,
    persistence_port: PermissionPersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> PermissionAPIGetMultipleResponseObject:
    try:
        query = await api_port.to_obj_get_multiple(api_request)
        many_permissions = await persistence_port.read_many(query)
        actor_id: str = await authc_port.get_actor_identifier(request)
        authz_result = await authz_port.authorize_operation(
            Actor(id=actor_id),
            OperationType.READ_RESOURCE,
            [
                Resource(
                    resource_type=ResourceType.PERMISSION,
                    name=permission.name,
                    namespace_name=permission.namespace_name,
                    app_name=permission.app_name,
                )
                for permission in many_permissions.objects
            ],
        )
        allowed_permissions = {
            resource_id
            for resource_id in authz_result.keys()
            if authz_result[resource_id]
        }
        return await api_port.to_api_get_multiple_response(
            [
                permission
                for permission in many_permissions.objects
                if Resource(
                    resource_type=ResourceType.PERMISSION,
                    name=permission.name,
                    namespace_name=permission.namespace_name,
                    app_name=permission.app_name,
                ).id
                in allowed_permissions
            ],
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> PermissionAPIGetSingleResponseObject:
    try:
        query, changed_values = await api_port.to_obj_edit(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.PERMISSION,
            name=query.name,
            namespace_name=query.namespace_name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.UPDATE_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to edit this permission."
            )
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> RoleSingleResponse:
    try:
        query = await role_api_port.to_role_get(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.ROLE,
            name=query.name,
            namespace_name=query.namespace_name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.READ_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to read this role."
            )
        role = await persistence_port.read_one(query)
        return await role_api_port.to_role_get_response(role)
    except Exception as exc:
        raise (await role_api_port.transform_exception(exc)) from exc


async def get_roles(
    api_request: RoleGetAllRequest | RoleGetByAppRequest | RoleGetByNamespaceRequest,
    role_api_port: RoleAPIPort,
    persistence_port: RolePersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> RoleMultipleResponse:
    try:
        query = await role_api_port.to_roles_get(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        many_roles = await persistence_port.read_many(query)
        authz_result = await authz_port.authorize_operation(
            Actor(id=actor_id),
            OperationType.READ_RESOURCE,
            [
                Resource(
                    resource_type=ResourceType.ROLE,
                    name=role.name,
                    namespace_name=role.namespace_name,
                    app_name=role.app_name,
                )
                for role in many_roles.objects
            ],
        )
        allowed_roles = {
            resource_id
            for resource_id in authz_result.keys()
            if authz_result[resource_id]
        }
        return await role_api_port.to_roles_get_response(
            roles=[
                role
                for role in many_roles.objects
                if Resource(
                    resource_type=ResourceType.ROLE,
                    name=role.name,
                    namespace_name=role.namespace_name,
                    app_name=role.app_name,
                ).id
                in allowed_roles
            ],
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> RoleSingleResponse:
    try:
        query = await role_api_port.to_role_create(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        role = query.roles[0]
        resource: Resource = Resource(
            resource_type=ResourceType.ROLE,
            name=role.name,
            namespace_name=role.namespace_name,
            app_name=role.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.CREATE_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to create this role."
            )
        created_role = await persistence_port.create(role)
        return await role_api_port.to_role_create_response(created_role)
    except Exception as exc:
        raise (await role_api_port.transform_exception(exc)) from exc


async def edit_role(
    api_request: RoleEditRequest,
    role_api_port: RoleAPIPort,
    persistence_port: RolePersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> RoleSingleResponse:
    try:
        query = await role_api_port.to_role_get(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.ROLE,
            name=query.name,
            namespace_name=query.namespace_name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.UPDATE_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to edit this role."
            )
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
):
    try:
        query = await api_port.to_context_create(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.CONTEXT,
            name=query.name,
            namespace_name=query.namespace_name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id), OperationType.CREATE_RESOURCE, [resource]
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to create this context."
            )
        created_context = await persistence_port.create(query)
        logger.bind(query=query, created_context=created_context).debug(
            "Context created."
        )
        return await api_port.to_api_create_response(created_context)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def get_context(
    api_request: ContextGetRequest,
    api_port: ContextAPIPort,
    persistence_port: ContextPersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> ContextSingleResponse:
    try:
        query = await api_port.to_context_get(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.CONTEXT,
            name=query.name,
            namespace_name=query.namespace_name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id), OperationType.READ_RESOURCE, [resource]
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to read this context."
            )
        context = await persistence_port.read_one(query)
        logger.bind(query=query, context=context).debug("Retrieved context.")
        return await api_port.to_api_get_response(context)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def get_contexts(
    api_request: ContextsAPIGetRequestObject,
    api_port: ContextAPIPort,
    persistence_port: ContextPersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> ContextMultipleResponse:
    try:
        query = await api_port.to_contexts_get(api_request)
        contexts = await persistence_port.read_many(query)
        logger.bind(query=query, contexts=contexts).debug("Retrieved contexts.")
        actor_id: str = await authc_port.get_actor_identifier(request)
        authz_result = await authz_port.authorize_operation(
            Actor(id=actor_id),
            OperationType.READ_RESOURCE,
            [
                Resource(
                    resource_type=ResourceType.CONTEXT,
                    name=context.name,
                    namespace_name=context.namespace_name,
                    app_name=context.app_name,
                )
                for context in contexts.objects
            ],
        )
        allowed_contexts = {
            resource_id
            for resource_id in authz_result.keys()
            if authz_result[resource_id]
        }
        return await api_port.to_api_contexts_get_response(
            [
                context
                for context in contexts.objects
                if Resource(
                    resource_type=ResourceType.CONTEXT,
                    name=context.name,
                    namespace_name=context.namespace_name,
                    app_name=context.app_name,
                ).id
                in allowed_contexts
            ],
            query.pagination.query_offset,
            query.pagination.query_limit
            if query.pagination.query_limit
            else contexts.total_count,
            contexts.total_count,
        )
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def edit_context(
    api_request: ContextEditRequest,
    api_port: ContextAPIPort,
    persistence_port: ContextPersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
):
    try:
        query, changed_values = await api_port.to_context_edit(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.CONTEXT,
            name=query.name,
            namespace_name=query.namespace_name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id), OperationType.UPDATE_RESOURCE, [resource]
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to edit this context."
            )
        obj = await persistence_port.read_one(query)
        for key, value in changed_values.items():
            setattr(obj, key, value)
        updated_context = await persistence_port.update(obj)
        logger.bind(query=query, updated_context=updated_context).debug(
            "Updated context."
        )
        return await api_port.to_api_edit_response(updated_context)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def get_namespaces_by_app(
    api_request: GetByAppRequest,
    namespace_api_port: FastAPINamespaceAPIAdapter,
    namespace_persistence_port: NamespacePersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
):
    try:
        query = await namespace_api_port.to_namespaces_by_appname_get(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        namespaces_persistence = await namespace_persistence_port.read_many(query)
        logger.bind(query=query, namespaces=namespaces_persistence).debug(
            "Retrieved Namespaces."
        )
        authz_result = await authz_port.authorize_operation(
            Actor(id=actor_id),
            OperationType.READ_RESOURCE,
            [
                Resource(
                    resource_type=ResourceType.NAMESPACE,
                    name=namespace.name,
                    app_name=namespace.app_name,
                )
                for namespace in namespaces_persistence.objects
            ],
        )
        allowed_namespaces = {
            resource_id
            for resource_id in authz_result.keys()
            if authz_result[resource_id]
        }
        return await namespace_api_port.to_api_namespaces_get_response(
            namespaces=[
                ns
                for ns in namespaces_persistence.objects
                if Resource(
                    resource_type=ResourceType.NAMESPACE,
                    name=ns.name,
                    app_name=ns.app_name,
                ).id
                in allowed_namespaces
            ],
            query_offset=query.pagination.query_offset,
            query_limit=query.pagination.query_limit
            if query.pagination.query_limit
            else namespaces_persistence.total_count,
            total_count=namespaces_persistence.total_count,
        )
    except Exception as exc:
        raise (
            await namespace_api_port.transform_exception(exc)
        ) from exc  # pragma: no cover


async def get_capability(
    api_request: APIGetSingleRequestObject,
    api_port: CapabilityAPIPort,
    persistence_port: CapabilityPersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
):
    try:
        query = await api_port.to_obj_get_single(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.CAPABILITY,
            name=query.name,
            namespace_name=query.namespace_name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.READ_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to read this capability."
            )
        capability = await persistence_port.read_one(query)
        return await api_port.to_api_get_single_response(capability)
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc


async def get_capabilities(
    api_request: APIGetMultipleRequestObject,
    api_port: CapabilityAPIPort,
    persistence_port: CapabilityPersistencePort,
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
) -> APIGetMultipleResponseObject:
    try:
        query = await api_port.to_obj_get_multiple(api_request)
        many_capabilities = await persistence_port.read_many(query)
        actor_id: str = await authc_port.get_actor_identifier(request)
        authz_result = await authz_port.authorize_operation(
            Actor(id=actor_id),
            OperationType.READ_RESOURCE,
            [
                Resource(
                    resource_type=ResourceType.CAPABILITY,
                    name=capability.name,
                    namespace_name=capability.namespace_name,
                    app_name=capability.app_name,
                )
                for capability in many_capabilities.objects
            ],
        )
        allowed_capabilities = {
            resource_id
            for resource_id in authz_result.keys()
            if authz_result[resource_id]
        }
        return await api_port.to_api_get_multiple_response(
            [
                capability
                for capability in many_capabilities.objects
                if Resource(
                    resource_type=ResourceType.CAPABILITY,
                    name=capability.name,
                    namespace_name=capability.namespace_name,
                    app_name=capability.app_name,
                ).id
                in allowed_capabilities
            ],
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
):
    try:
        query = await api_port.to_obj_create(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.CAPABILITY,
            name=query.name,
            namespace_name=query.namespace_name,
            app_name=query.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.CREATE_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to create this capability."
            )
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
):
    try:
        edited_capability = await api_port.to_obj_edit(api_request)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.CAPABILITY,
            name=edited_capability.name,
            namespace_name=edited_capability.namespace_name,
            app_name=edited_capability.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.UPDATE_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to update this capability."
            )
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
    authc_port: AuthenticationPort,
    authz_port: ResourceAuthorizationPort,
    request: Request,
):
    try:
        query = await api_port.to_obj_get_single(api_request)
        capability = await persistence_port.read_one(query)
        actor_id: str = await authc_port.get_actor_identifier(request)
        resource: Resource = Resource(
            resource_type=ResourceType.CAPABILITY,
            name=capability.name,
            namespace_name=capability.namespace_name,
            app_name=capability.app_name,
        )
        allowed = (
            await authz_port.authorize_operation(
                Actor(id=actor_id),
                OperationType.DELETE_RESOURCE,
                [resource],
            )
        ).get(resource.id, False)
        if not allowed:
            raise UnauthorizedError(
                "The logged in user is not authorized to delete this capability."
            )
        await persistence_port.delete(query)
        await bundle_server_port.schedule_bundle_build(BundleType.data)
        return None
    except Exception as exc:
        raise (await api_port.transform_exception(exc)) from exc
