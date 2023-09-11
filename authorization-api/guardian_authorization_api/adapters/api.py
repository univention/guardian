# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from ..models.policies import (
    Context as PoliciesContext,
)
from ..models.policies import (
    GetPermissionsQuery,
    GetPermissionsResult,
    PolicyObject,
)
from ..models.policies import Namespace as PoliciesNamespace
from ..models.policies import Role as PoliciesRole
from ..models.policies import Target as PoliciesTarget
from ..models.routes import (
    AppName,
    AuthzObject,
    AuthzObjectIdentifier,
    AuthzPermissionsPostRequest,
    AuthzPermissionsPostResponse,
    Context,
    NamespaceMinimal,
    NamespaceName,
    Permission,
    PermissionName,
    PermissionResult,
    Target,
)
from ..ports import GetPermissionsAPIPort


class FastAPIGetPermissionsAPIAdapter(GetPermissionsAPIPort):
    @staticmethod
    def _to_policy_object(obj: AuthzObject) -> PolicyObject:
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
    def _to_policy_target(target: Target) -> PoliciesTarget:
        old_target = (
            FastAPIGetPermissionsAPIAdapter._to_policy_object(target.old_target)
            if target.old_target
            else None
        )
        new_target = (
            FastAPIGetPermissionsAPIAdapter._to_policy_object(target.new_target)
            if target.new_target
            else None
        )
        return PoliciesTarget(
            old_target=old_target,
            new_target=new_target,
        )

    @staticmethod
    def _to_policy_namespace(namespace: NamespaceMinimal) -> PoliciesNamespace:
        return PoliciesNamespace(app_name=namespace.app_name, name=namespace.name)

    @staticmethod
    def _to_policy_context(context: Context) -> PoliciesContext:
        return PoliciesContext(
            app_name=context.app_name,
            namespace_name=context.namespace_name,
            name=context.name,
        )

    async def to_policy_query(
        self, api_request: AuthzPermissionsPostRequest
    ) -> GetPermissionsQuery:
        targets = (
            [self._to_policy_target(target) for target in api_request.targets]
            if api_request.targets
            else []
        )
        namespaces = (
            [
                self._to_policy_namespace(namespace)
                for namespace in api_request.namespaces
            ]
            if api_request.namespaces
            else []
        )
        contexts = (
            [self._to_policy_context(context) for context in api_request.contexts]
            if api_request.contexts
            else []
        )
        return GetPermissionsQuery(
            actor=self._to_policy_object(api_request.actor),
            targets=targets,
            namespaces=namespaces,
            contexts=contexts,
            extra_args=api_request.extra_request_data,
            include_general_permissions=api_request.include_general_permissions,
        )

    async def to_policy_query_with_lookup(
        self, api_request: AuthzPermissionsPostRequest, actor, targets
    ) -> GetPermissionsQuery:
        def _funky_to_policy_object(obj):
            new_target = (
                FastAPIGetPermissionsAPIAdapter._to_policy_object(obj.new_target)
                if api_request.targets[0].new_target
                else None
            )
            old_target_id = obj.old_target.id
            return old_target_id, new_target

        namespaces = (
            [
                self._to_policy_namespace(namespace)
                for namespace in api_request.namespaces
            ]
            if api_request.namespaces
            else []
        )
        contexts = (
            [self._to_policy_context(context) for context in api_request.contexts]
            if api_request.contexts
            else []
        )
        breakpoint()
        return GetPermissionsQuery(
            actor=self._to_policy_object(actor),
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
