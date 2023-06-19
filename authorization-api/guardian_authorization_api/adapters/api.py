from ..models.policies import Context as PoliciesContext
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
    AuthzPermissionsPostRequest,
    AuthzPermissionsPostResponse,
    Context,
    NamespaceMinimal,
    NamespaceName,
    Object,
    ObjectIdentifier,
    Permission,
    PermissionName,
    PermissionResult,
    Target,
)
from ..ports import GetPermissionsAPIPort


class FastAPIGetPermissionsAPIAdapter(GetPermissionsAPIPort):
    @staticmethod
    def _to_policy_object(obj: Object) -> PolicyObject:
        return PolicyObject(
            id=str(obj.id),
            roles=[
                PoliciesRole(
                    app_name=role.app_name,
                    namespace_name=role.app_name,
                    name=role.name,
                )
                for role in obj.roles
            ],
            attributes=obj.attributes,
        )

    @staticmethod
    def _to_policy_target(target: Target) -> PoliciesTarget:
        return PoliciesTarget(
            old_target=FastAPIGetPermissionsAPIAdapter._to_policy_object(
                target.old_target
            )
            if target.old_target
            else None,
            new_target=FastAPIGetPermissionsAPIAdapter._to_policy_object(
                target.new_target
            )
            if target.new_target
            else None,
        )

    @staticmethod
    def _to_policy_namespace(namespace: NamespaceMinimal) -> PoliciesNamespace:
        return PoliciesNamespace(
            app_name=namespace.app_name, name=namespace.namespace_name
        )

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
        return GetPermissionsQuery(
            actor=self._to_policy_object(api_request.actor),
            targets=[self._to_policy_target(target) for target in api_request.targets]
            if api_request.targets
            else [],
            namespaces=[
                self._to_policy_namespace(namespace)
                for namespace in api_request.namespaces
            ]
            if api_request.namespaces
            else [],
            contexts=[
                self._to_policy_context(context) for context in api_request.contexts
            ]
            if api_request.contexts
            else [],
            extra_args=api_request.extra_request_data,
            include_general_permissions=api_request.include_general_permissions,
        )

    async def to_api_response(
        self, permissions_result: GetPermissionsResult
    ) -> AuthzPermissionsPostResponse:
        target_permissions = [
            PermissionResult(
                target_id=ObjectIdentifier(target_p.target_id),
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
            actor_id=ObjectIdentifier(permissions_result.actor.id),
            target_permissions=target_permissions,
            general_permissions=general_permissions,
        )
