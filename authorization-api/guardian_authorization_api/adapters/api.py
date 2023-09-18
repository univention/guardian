# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
import typing
from typing import Optional

from fastapi import HTTPException

from ..errors import ObjectNotFoundError, PersistenceError, PolicyUpstreamError
from ..models.persistence import PersistenceObject
from ..models.policies import (
    CheckPermissionsQuery,
    CheckPermissionsResult,
    GetPermissionsQuery,
    GetPermissionsResult,
    PolicyObject,
)
from ..models.policies import Context as PoliciesContext
from ..models.policies import Namespace as PoliciesNamespace
from ..models.policies import Permission as PoliciesPermission
from ..models.policies import Role as PoliciesRole
from ..models.policies import Target as PoliciesTarget
from ..models.routes import (
    AppName,
    AuthzObject,
    AuthzObjectIdentifier,
    AuthzPermissionsCheckLookupPostRequest,
    AuthzPermissionsCheckPostRequest,
    AuthzPermissionsCheckPostResponse,
    AuthzPermissionsLookupPostRequest,
    AuthzPermissionsPostRequest,
    AuthzPermissionsPostResponse,
    Context,
    NamespaceMinimal,
    NamespaceName,
    Permission,
    PermissionCheckResult,
    PermissionName,
    PermissionResult,
    Target,
    TargetLookup,
)
from ..ports import CheckPermissionsAPIPort, GetPermissionsAPIPort


class TransformExceptionMixin:
    logger: typing.Any

    async def transform_exception(self, exc: Exception) -> HTTPException:
        self.logger.exception(exc)
        if isinstance(exc, PolicyUpstreamError) or isinstance(exc, PersistenceError):
            return HTTPException(status_code=500, detail={"message": str(exc)})
        elif isinstance(exc, ObjectNotFoundError):
            return HTTPException(status_code=404, detail={"message": str(exc)})
        else:
            return HTTPException(
                status_code=500, detail={"message": "Internal server error."}
            )


class FastAPIAdapterUtils:
    @staticmethod
    def authz_to_policy_object(obj: AuthzObject) -> PolicyObject:
        roles = [
            PoliciesRole(
                app_name=role.app_name,
                namespace_name=role.namespace_name,
                name=role.name,
            )
            for role in obj.roles
        ]
        return PolicyObject(
            id=str(obj.id),
            roles=roles,
            attributes=obj.attributes,
        )

    @staticmethod
    def api_target_to_policy_target(target: Target) -> PoliciesTarget:
        old_target = (
            FastAPIAdapterUtils.authz_to_policy_object(target.old_target)
            if target.old_target
            else None
        )
        new_target = (
            FastAPIAdapterUtils.authz_to_policy_object(target.new_target)
            if target.new_target
            else None
        )
        return PoliciesTarget(
            old_target=old_target,
            new_target=new_target,
        )

    @staticmethod
    def persistence_object_to_policy_object(po: PersistenceObject) -> PolicyObject:
        roles = []
        for app, namespace, role in [role.split(":") for role in po.roles]:
            roles.append(
                PoliciesRole(app_name=app, namespace_name=namespace, name=role)
            )
        if "guardianRole" in po.attributes:
            po.attributes.pop("guardianRole")
        return PolicyObject(id=po.id, roles=roles, attributes=po.attributes)

    @staticmethod
    def persistence_target_to_policy_target(
        old_target: PersistenceObject, new_target: AuthzObject
    ):
        po_old_target = (
            FastAPIAdapterUtils.persistence_object_to_policy_object(old_target)
            if old_target
            else None
        )
        po_new_target = (
            FastAPIAdapterUtils.authz_to_policy_object(new_target)
            if new_target
            else None
        )
        return PoliciesTarget(
            old_target=po_old_target,
            new_target=po_new_target,
        )

    @staticmethod
    def api_targets_to_policy_targets(
        targets: Optional[list[Target]],
    ) -> list[PoliciesTarget]:
        return (
            [
                FastAPIAdapterUtils.api_target_to_policy_target(target)
                for target in targets
            ]
            if targets
            else []
        )

    @staticmethod
    def api_contexts_to_policy_contexts(
        contexts: Optional[list[Context]],
    ) -> list[PoliciesContext]:
        return (
            [
                FastAPIAdapterUtils.api_context_to_policy_context(context)
                for context in contexts
            ]
            if contexts
            else []
        )

    @staticmethod
    def api_namespaces_to_policy_namespaces(
        namespaces: Optional[list[NamespaceMinimal]],
    ) -> Optional[list[PoliciesNamespace]]:
        return (
            [
                FastAPIAdapterUtils.api_namespace_to_policy_namespace(namespace)
                for namespace in namespaces
            ]
            if namespaces
            else None
        )

    @staticmethod
    def api_namespace_to_policy_namespace(
        namespace: NamespaceMinimal,
    ) -> PoliciesNamespace:
        return PoliciesNamespace(app_name=namespace.app_name, name=namespace.name)

    @staticmethod
    def api_context_to_policy_context(context: Context) -> PoliciesContext:
        return PoliciesContext(
            app_name=context.app_name,
            namespace_name=context.namespace_name,
            name=context.name,
        )

    @staticmethod
    def persistence_targets_to_policy_targets(targets):
        return (
            [
                FastAPIAdapterUtils.persistence_target_to_policy_target(
                    old_target=old_target, new_target=new_target
                )
                for old_target, new_target in targets
            ]
            if targets
            else []
        )


class FastAPIGetPermissionsAPIAdapter(TransformExceptionMixin, GetPermissionsAPIPort):
    async def to_policy_query(
        self, api_request: AuthzPermissionsPostRequest
    ) -> GetPermissionsQuery:
        targets = FastAPIAdapterUtils.api_targets_to_policy_targets(api_request.targets)
        namespaces = FastAPIAdapterUtils.api_namespaces_to_policy_namespaces(
            api_request.namespaces
        )
        contexts = FastAPIAdapterUtils.api_contexts_to_policy_contexts(
            api_request.contexts
        )

        return GetPermissionsQuery(
            actor=FastAPIAdapterUtils.authz_to_policy_object(api_request.actor),
            targets=targets,
            namespaces=namespaces,
            contexts=contexts,
            extra_args=api_request.extra_request_data,
            include_general_permissions=api_request.include_general_permissions,
        )

    async def to_policy_lookup_query(
        self,
        api_request: AuthzPermissionsLookupPostRequest,
        actor: PersistenceObject,
        targets: list[typing.Tuple[PersistenceObject, TargetLookup]],
    ) -> GetPermissionsQuery:
        _actor = FastAPIAdapterUtils.persistence_object_to_policy_object(actor)
        _targets = FastAPIAdapterUtils.persistence_targets_to_policy_targets(targets)
        contexts = FastAPIAdapterUtils.api_contexts_to_policy_contexts(
            api_request.contexts
        )
        namespaces = FastAPIAdapterUtils.api_namespaces_to_policy_namespaces(
            api_request.namespaces
        )
        return GetPermissionsQuery(
            actor=_actor,
            targets=_targets,
            namespaces=namespaces,
            contexts=contexts,
            extra_args=api_request.extra_request_data,
            include_general_permissions=api_request.include_general_permissions,
        )

    async def to_api_response(
        self, permissions_result: GetPermissionsResult
    ) -> AuthzPermissionsPostResponse:
        target_permissions = [
            PermissionResult(
                target_id=AuthzObjectIdentifier(target_p.target_id),
                permissions=[
                    Permission(
                        name=PermissionName(perm.name),
                        namespace_name=NamespaceName(perm.namespace_name),
                        app_name=AppName(perm.app_name),
                    )
                    for perm in target_p.permissions
                ],
            )
            for target_p in permissions_result.target_permissions
        ]
        general_permissions = (
            [
                Permission(
                    app_name=AppName(perm.app_name),
                    namespace_name=NamespaceName(perm.namespace_name),
                    name=PermissionName(perm.name),
                )
                for perm in permissions_result.general_permissions
            ]
            if permissions_result.general_permissions
            else []
        )
        return AuthzPermissionsPostResponse(
            actor_id=AuthzObjectIdentifier(permissions_result.actor.id),
            target_permissions=target_permissions,
            general_permissions=general_permissions,
        )


class FastAPICheckPermissionsAPIAdapter(
    TransformExceptionMixin, CheckPermissionsAPIPort
):
    async def to_api_response(
        self, actor_id: AuthzObjectIdentifier, check_result: CheckPermissionsResult
    ) -> AuthzPermissionsCheckPostResponse:
        permissions_check_results = [
            PermissionCheckResult(
                target_id=AuthzObjectIdentifier(check_result.target_id),
                actor_has_permissions=check_result.actor_has_permissions,
            )
            for check_result in check_result.target_permissions
        ]
        actor_has_all_permissions = (
            all(
                [
                    check_result.actor_has_permissions
                    for check_result in check_result.target_permissions
                ]
            )
            if check_result.target_permissions
            else False
        )

        return AuthzPermissionsCheckPostResponse(
            actor_id=actor_id,
            permissions_check_results=permissions_check_results,
            actor_has_all_targeted_permissions=actor_has_all_permissions,
            actor_has_all_general_permissions=check_result.actor_has_general_permissions,
        )

    async def to_policy_query(
        self, api_request: AuthzPermissionsCheckPostRequest
    ) -> CheckPermissionsQuery:
        actor = PolicyObject(
            id=api_request.actor.id,
            roles=[
                PoliciesRole(role.app_name, role.namespace_name, role.name)
                for role in api_request.actor.roles
            ],
            attributes=api_request.actor.attributes,
        )

        targets = FastAPIAdapterUtils.api_targets_to_policy_targets(api_request.targets)
        contexts = FastAPIAdapterUtils.api_contexts_to_policy_contexts(
            api_request.contexts
        )

        namespaces = FastAPIAdapterUtils.api_namespaces_to_policy_namespaces(
            api_request.namespaces
        )

        return CheckPermissionsQuery(
            actor=actor,
            contexts=contexts,
            targets=targets,
            namespaces=namespaces,
            target_permissions=[
                PoliciesPermission(
                    app_name=permission.app_name,
                    namespace_name=permission.namespace_name,
                    name=permission.name,
                )
                for permission in api_request.targeted_permissions_to_check
            ],
            general_permissions=[
                PoliciesPermission(
                    app_name=permission.app_name,
                    namespace_name=permission.namespace_name,
                    name=permission.name,
                )
                for permission in api_request.general_permissions_to_check
            ],
            extra_args=api_request.extra_request_data,
        )

    async def to_policy_lookup_query(
        self,
        api_request: AuthzPermissionsCheckLookupPostRequest,
        actor: PersistenceObject,
        targets: list[typing.Tuple[PersistenceObject, TargetLookup]],
    ) -> CheckPermissionsQuery:
        po_actor = FastAPIAdapterUtils.persistence_object_to_policy_object(actor)
        po_targets = FastAPIAdapterUtils.persistence_targets_to_policy_targets(targets)
        contexts = FastAPIAdapterUtils.api_contexts_to_policy_contexts(
            api_request.contexts
        )
        namespaces = FastAPIAdapterUtils.api_namespaces_to_policy_namespaces(
            api_request.namespaces
        )
        return CheckPermissionsQuery(
            actor=po_actor,
            contexts=contexts,
            targets=po_targets,
            namespaces=namespaces,
            target_permissions=[
                PoliciesPermission(
                    app_name=permission.app_name,
                    namespace_name=permission.namespace_name,
                    name=permission.name,
                )
                for permission in api_request.targeted_permissions_to_check
            ],
            general_permissions=[
                PoliciesPermission(
                    app_name=permission.app_name,
                    namespace_name=permission.namespace_name,
                    name=permission.name,
                )
                for permission in api_request.general_permissions_to_check
            ],
            extra_args=api_request.extra_request_data,
        )
