# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only
import typing
from typing import Optional

from fastapi import HTTPException
from pydantic import ValidationError

from ..errors import ObjectNotFoundError, PersistenceError, PolicyUpstreamError
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
    AuthzObjectLookup,
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
from ..ports import (
    CheckPermissionsAPIPort,
    GetPermissionsAPIPort,
)


class TransformExceptionMixin:
    logger: typing.Any

    async def transform_exception(self, exc: Exception) -> HTTPException:
        self.logger.exception(exc)
        if isinstance(exc, PolicyUpstreamError) or isinstance(exc, PersistenceError):
            return HTTPException(status_code=500, detail={"message": str(exc)})
        elif isinstance(exc, ObjectNotFoundError):
            return HTTPException(status_code=404, detail={"message": str(exc)})
        elif isinstance(exc, ValidationError):
            return HTTPException(status_code=422, detail={"message": str(exc)})
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
                context=(
                    PoliciesContext(
                        app_name=role.context.app_name,
                        namespace_name=role.context.namespace_name,
                        name=role.context.name,
                    )
                    if role.context
                    else None
                ),
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
    def api_look_up_target_to_policy_target(
        old_target: Optional[PolicyObject], request_target: Target | TargetLookup
    ):
        # old_target can be either: None or provided by persistence layer or request
        if isinstance(request_target.old_target, AuthzObject):
            return FastAPIAdapterUtils.api_target_to_policy_target(request_target)
        else:
            return PoliciesTarget(
                new_target=(
                    FastAPIAdapterUtils.authz_to_policy_object(
                        request_target.new_target
                    )
                    if request_target.new_target
                    else None
                ),
                old_target=old_target,
            )

    @staticmethod
    def api_lookup_targets_to_policy_targets(
        old_lookup_targets: list[PolicyObject | None],
        api_request_targets: Optional[list[Target | TargetLookup]],
    ):
        targets = []
        if api_request_targets:
            for old_target, request_target in zip(
                old_lookup_targets, api_request_targets
            ):
                targets.append(
                    FastAPIAdapterUtils.api_look_up_target_to_policy_target(
                        old_target=old_target, request_target=request_target
                    )
                )
        return targets

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

    async def to_policy_lookup_query(
        self,
        api_request: AuthzPermissionsLookupPostRequest,
        actor: PolicyObject,
        old_looked_up_targets: list[PolicyObject | None],
    ) -> GetPermissionsQuery:
        namespaces = FastAPIAdapterUtils.api_namespaces_to_policy_namespaces(
            api_request.namespaces
        )
        contexts = FastAPIAdapterUtils.api_contexts_to_policy_contexts(
            api_request.contexts
        )
        targets = FastAPIAdapterUtils.api_lookup_targets_to_policy_targets(
            old_lookup_targets=old_looked_up_targets,
            api_request_targets=api_request.targets,
        )
        return GetPermissionsQuery(
            actor=actor,
            targets=targets,
            namespaces=namespaces,
            contexts=contexts,
            extra_args=api_request.extra_request_data,
            include_general_permissions=api_request.include_general_permissions,
        )

    @staticmethod
    def get_actor_and_target_ids(
        api_request: AuthzPermissionsLookupPostRequest,
    ) -> tuple[str, list[str | None]]:
        target_ids = []
        if api_request.targets:
            target_ids = [
                (
                    str(target.old_target.id)
                    if isinstance(target.old_target, AuthzObjectLookup)
                    else None
                )
                for target in api_request.targets
            ]
        return str(api_request.actor.id), target_ids


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
        actor: PolicyObject,
        old_looked_up_targets: list[PolicyObject | None],
    ) -> CheckPermissionsQuery:
        contexts = FastAPIAdapterUtils.api_contexts_to_policy_contexts(
            api_request.contexts
        )
        namespaces = FastAPIAdapterUtils.api_namespaces_to_policy_namespaces(
            api_request.namespaces
        )
        targets = FastAPIAdapterUtils.api_lookup_targets_to_policy_targets(
            old_lookup_targets=old_looked_up_targets,
            api_request_targets=api_request.targets,
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

    @staticmethod
    def get_actor_and_target_ids(
        api_request: AuthzPermissionsCheckLookupPostRequest,
    ) -> tuple[str, list[str | None]]:
        target_ids = []
        if api_request.targets:
            target_ids = [
                (
                    str(target.old_target.id)
                    if isinstance(target.old_target, AuthzObjectLookup)
                    else None
                )
                for target in api_request.targets
            ]
        return str(api_request.actor.id), target_ids
