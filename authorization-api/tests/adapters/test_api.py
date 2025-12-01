# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Callable

import pytest
from guardian_authorization_api.adapters.api import (
    FastAPIAdapterUtils,
    FastAPICheckPermissionsAPIAdapter,
    FastAPIGetPermissionsAPIAdapter,
)
from guardian_authorization_api.models.policies import (
    CheckPermissionsQuery,
    CheckPermissionsResult,
    CheckResult,
    GetPermissionsQuery,
    GetPermissionsResult,
    PolicyObject,
    TargetPermissions,
)
from guardian_authorization_api.models.policies import (
    Context as PoliciesContext,
)
from guardian_authorization_api.models.policies import Namespace as PoliciesNamespace
from guardian_authorization_api.models.policies import Permission as PoliciesPermission
from guardian_authorization_api.models.policies import Role as PoliciesRole
from guardian_authorization_api.models.policies import Target as PoliciesTarget
from guardian_authorization_api.models.routes import (
    Actor,
    AppName,
    AuthzObject,
    AuthzObjectIdentifier,
    AuthzPermissionsCheckPostRequest,
    AuthzPermissionsCheckPostResponse,
    AuthzPermissionsPostRequest,
    AuthzPermissionsPostResponse,
    Context,
    ContextName,
    NamespaceMinimal,
    NamespaceName,
    Permission,
    PermissionCheckResult,
    PermissionName,
    PermissionResult,
    Role,
    Target,
)

from ..conftest import get_authz_permissions_check_request_dict


@pytest.fixture
def get_route_object() -> Callable[[], AuthzObject]:
    def _get_route_object() -> AuthzObject:
        return AuthzObject(
            id=AuthzObjectIdentifier("test-id"),
            roles=[
                Role(
                    app_name=AppName("app"),
                    namespace_name=NamespaceName("namespace"),
                    name=AuthzObjectIdentifier("role"),
                )
            ],
            attributes={"a": "b"},
        )

    return _get_route_object


class TestFastAPICheckPermissionsAPIAdapter:
    @pytest.fixture
    def adapter_instance(self):
        return FastAPICheckPermissionsAPIAdapter()

    @pytest.mark.asyncio
    async def test_to_api_response(self, adapter_instance):
        permissions_check_result = CheckPermissionsResult(
            [CheckResult(target_id="id1", actor_has_permissions=True)],
            actor_has_general_permissions=True,
        )

        result = await adapter_instance.to_api_response(
            AuthzObjectIdentifier("id2"), permissions_check_result
        )

        assert result == AuthzPermissionsCheckPostResponse(
            actor_id=AuthzObjectIdentifier("id2"),
            permissions_check_results=[
                PermissionCheckResult(
                    target_id=AuthzObjectIdentifier("id1"), actor_has_permissions=True
                )
            ],
            actor_has_all_targeted_permissions=True,
            actor_has_all_general_permissions=True,
        )

    @pytest.mark.asyncio
    async def test_to_policy_query(self, adapter_instance):
        data = get_authz_permissions_check_request_dict()
        permissions_check_result = AuthzPermissionsCheckPostRequest.model_validate(data)

        query = await adapter_instance.to_policy_query(permissions_check_result)

        assert query == CheckPermissionsQuery(
            actor=PolicyObject(
                id=data["actor"]["id"],
                roles=[
                    PoliciesRole(
                        app_name=AppName(role["app_name"]),
                        namespace_name=NamespaceName(role["namespace_name"]),
                        name=AuthzObjectIdentifier(role["name"]),
                    )
                    for role in data["actor"]["roles"]
                ],
                attributes=data["actor"]["attributes"],
            ),
            targets=[
                PoliciesTarget(
                    old_target=PolicyObject(
                        id=target["old_target"]["id"],
                        roles=[
                            PoliciesRole(
                                app_name=AppName(role["app_name"]),
                                namespace_name=NamespaceName(role["namespace_name"]),
                                name=AuthzObjectIdentifier(role["name"]),
                            )
                            for role in target["old_target"]["roles"]
                        ],
                        attributes=target["old_target"]["attributes"],
                    ),
                    new_target=PolicyObject(
                        id=target["new_target"]["id"],
                        roles=[
                            PoliciesRole(
                                app_name=AppName(role["app_name"]),
                                namespace_name=NamespaceName(role["namespace_name"]),
                                name=AuthzObjectIdentifier(role["name"]),
                            )
                            for role in target["new_target"]["roles"]
                        ],
                        attributes=target["new_target"]["attributes"],
                    ),
                )
                for target in data["targets"]
            ],
            namespaces=[
                PoliciesNamespace(
                    app_name=AppName(namespace["app_name"]),
                    name=NamespaceName(namespace["name"]),
                )
                for namespace in data["namespaces"]
            ],
            target_permissions=[
                PoliciesPermission(
                    app_name=AppName(permission["app_name"]),
                    namespace_name=NamespaceName(permission["namespace_name"]),
                    name=PermissionName(permission["name"]),
                )
                for permission in data["targeted_permissions_to_check"]
            ],
            general_permissions=[
                PoliciesPermission(
                    app_name=AppName(permission["app_name"]),
                    namespace_name=NamespaceName(permission["namespace_name"]),
                    name=PermissionName(permission["name"]),
                )
                for permission in data["general_permissions_to_check"]
            ],
            contexts=[
                PoliciesContext(
                    app_name=AppName(context["app_name"]),
                    namespace_name=NamespaceName(context["namespace_name"]),
                    name=PermissionName(context["name"]),
                )
                for context in data["contexts"]
            ],
            extra_args=data["extra_request_data"],
        )


class TestFastAPIGetPermissionsAPIAdapter:
    @pytest.fixture
    def adapter_instance(self):
        return FastAPIGetPermissionsAPIAdapter()

    def test_to_policy_object(self, get_route_object):
        obj = get_route_object()
        result = FastAPIAdapterUtils.authz_to_policy_object(obj)
        assert result == PolicyObject(
            id="test-id",
            roles=[
                PoliciesRole(app_name="app", namespace_name="namespace", name="role")
            ],
            attributes={"a": "b"},
        )

    @pytest.mark.parametrize(
        "has_old,has_new", [(True, True), (False, False), (True, False), (False, True)]
    )
    def test_to_policy_target(self, has_old, has_new, get_route_object):
        old = get_route_object() if has_old else None
        new = get_route_object() if has_new else None
        expected_policy_obj = PolicyObject(
            id="test-id",
            roles=[
                PoliciesRole(app_name="app", namespace_name="namespace", name="role")
            ],
            attributes={"a": "b"},
        )
        target = Target(old_target=old, new_target=new)
        result = FastAPIAdapterUtils.api_target_to_policy_target(target)
        if has_new:
            assert result.new_target == expected_policy_obj
        else:
            assert result.new_target is None
        if has_old:
            assert result.old_target == expected_policy_obj
        else:
            assert result.old_target is None

    def test_to_policy_namespace(self):
        input_ns = NamespaceMinimal(
            app_name=AppName("app"), name=NamespaceName("namespace")
        )
        result = FastAPIAdapterUtils.api_namespace_to_policy_namespace(input_ns)
        assert result == PoliciesNamespace(app_name="app", name="namespace")

    def test_to_policy_context(self):
        input_ctx = Context(
            app_name=AppName("app"),
            namespace_name=NamespaceName("namespace"),
            name=ContextName("context"),
        )
        result = FastAPIAdapterUtils.api_context_to_policy_context(input_ctx)
        assert result == PoliciesContext(
            app_name="app", namespace_name="namespace", name="context"
        )

    @pytest.mark.asyncio
    async def test_to_policy_query(self, get_route_object, adapter_instance):
        input_obj = AuthzPermissionsPostRequest(
            namespaces=[
                NamespaceMinimal(
                    app_name=AppName("app"), name=NamespaceName("namespace")
                )
            ],
            actor=Actor(**get_route_object().model_dump()),
            targets=[
                Target(old_target=get_route_object(), new_target=get_route_object())
            ],
            contexts=[
                Context(
                    app_name=AppName("app"),
                    namespace_name=NamespaceName("namespace"),
                    name=ContextName("context"),
                )
            ],
            include_general_permissions=True,
            extra_request_data={"a": "b"},
        )
        result = await adapter_instance.to_policy_query(input_obj)
        assert result == GetPermissionsQuery(
            actor=PolicyObject(
                id="test-id",
                roles=[
                    PoliciesRole(
                        app_name="app", namespace_name="namespace", name="role"
                    )
                ],
                attributes={"a": "b"},
            ),
            targets=[
                PoliciesTarget(
                    old_target=PolicyObject(
                        id="test-id",
                        roles=[
                            PoliciesRole(
                                app_name="app", namespace_name="namespace", name="role"
                            )
                        ],
                        attributes={"a": "b"},
                    ),
                    new_target=PolicyObject(
                        id="test-id",
                        roles=[
                            PoliciesRole(
                                app_name="app", namespace_name="namespace", name="role"
                            )
                        ],
                        attributes={"a": "b"},
                    ),
                )
            ],
            namespaces=[PoliciesNamespace(app_name="app", name="namespace")],
            contexts=[
                PoliciesContext(
                    app_name="app", namespace_name="namespace", name="context"
                )
            ],
            extra_args={"a": "b"},
            include_general_permissions=True,
        )

    @pytest.mark.asyncio
    async def test_to_api_response(self, adapter_instance):
        input_obj = GetPermissionsResult(
            actor=PolicyObject(
                id="test-id",
                roles=[
                    PoliciesRole(
                        app_name="app", namespace_name="namespace", name="role"
                    )
                ],
                attributes={"a": "b"},
            ),
            target_permissions=[
                TargetPermissions(
                    target_id="test-id",
                    permissions=[
                        PoliciesPermission(
                            app_name="app",
                            namespace_name="namespace",
                            name="permission",
                        )
                    ],
                )
            ],
            general_permissions=[
                PoliciesPermission(
                    app_name="app",
                    namespace_name="namespace",
                    name="permission2",
                )
            ],
        )
        result = await adapter_instance.to_api_response(input_obj)
        assert result == AuthzPermissionsPostResponse(
            actor_id=AuthzObjectIdentifier("test-id"),
            target_permissions=[
                PermissionResult(
                    target_id=AuthzObjectIdentifier("test-id"),
                    permissions=[
                        Permission(
                            app_name=AppName("app"),
                            namespace_name=NamespaceName("namespace"),
                            name=PermissionName("permission"),
                        )
                    ],
                )
            ],
            general_permissions=[
                Permission(
                    app_name=AppName("app"),
                    namespace_name=NamespaceName("namespace"),
                    name=PermissionName("permission2"),
                )
            ],
        )


class TestFastAPIAdapterUtils:
    @pytest.mark.parametrize(
        "context",
        [
            Context(
                app_name=AppName("app"),
                namespace_name=NamespaceName("namespace"),
                name=ContextName("context"),
            ),
            None,
        ],
    )
    def test_preserve_context(self, context):
        authz_obj = AuthzObject(
            id=AuthzObjectIdentifier("test-id"),
            roles=[
                Role(
                    app_name=AppName("app"),
                    namespace_name=NamespaceName("namespace"),
                    name=AuthzObjectIdentifier("role"),
                    context=context,
                )
            ],
            attributes={},
        )
        result = FastAPIAdapterUtils.authz_to_policy_object(authz_obj)
        assert result == PolicyObject(
            id="test-id",
            roles=[
                PoliciesRole(
                    app_name="app",
                    namespace_name="namespace",
                    name="role",
                    context=(
                        PoliciesContext(
                            app_name=context.app_name,
                            namespace_name=context.namespace_name,
                            name=context.name,
                        )
                        if context
                        else None
                    ),
                )
            ],
            attributes={},
        )
