# Copyright (C) 2023 Univention GmbH
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Callable

import pytest
from guardian_authorization_api.adapters.api import FastAPIGetPermissionsAPIAdapter
from guardian_authorization_api.models.policies import (
    Context as PoliciesContext,
)
from guardian_authorization_api.models.policies import (
    GetPermissionsQuery,
    GetPermissionsResult,
    PolicyObject,
    TargetPermissions,
)
from guardian_authorization_api.models.policies import Namespace as PoliciesNamespace
from guardian_authorization_api.models.policies import Permission as PoliciesPermission
from guardian_authorization_api.models.policies import Role as PoliciesRole
from guardian_authorization_api.models.policies import Target as PoliciesTarget
from guardian_authorization_api.models.routes import (
    Actor,
    AppName,
    AuthzPermissionsPostRequest,
    AuthzPermissionsPostResponse,
    Context,
    ContextDisplayName,
    ContextName,
    NamespaceMinimal,
    NamespaceName,
    Object,
    ObjectIdentifier,
    Permission,
    PermissionName,
    PermissionResult,
    Role,
    Target,
)


@pytest.fixture
def get_route_object() -> Callable[[], Object]:
    def _get_route_object() -> Object:
        return Object(
            id=ObjectIdentifier("id"),
            roles=[
                Role(
                    app_name=AppName("app"),
                    namespace_name=NamespaceName("namespace"),
                    name=ObjectIdentifier("role"),
                )
            ],
            attributes={"a": "b"},
        )

    return _get_route_object


class TestFastAPIGetPermissionsAPIAdapter:
    @pytest.fixture
    def adapter_instance(self):
        return FastAPIGetPermissionsAPIAdapter()

    def test_to_policy_object(self, get_route_object):
        obj = get_route_object()
        result = FastAPIGetPermissionsAPIAdapter._to_policy_object(obj)
        assert result == PolicyObject(
            id="id",
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
            id="id",
            roles=[
                PoliciesRole(app_name="app", namespace_name="namespace", name="role")
            ],
            attributes={"a": "b"},
        )
        target = Target(old_target=old, new_target=new)
        result = FastAPIGetPermissionsAPIAdapter._to_policy_target(target)
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
        result = FastAPIGetPermissionsAPIAdapter._to_policy_namespace(input_ns)
        assert result == PoliciesNamespace(app_name="app", name="namespace")

    def test_to_policy_context(self):
        input_ctx = Context(
            app_name=AppName("app"),
            namespace_name=NamespaceName("namespace"),
            name=ContextName("context"),
            displayname=ContextDisplayName("ctx"),
        )
        result = FastAPIGetPermissionsAPIAdapter._to_policy_context(input_ctx)
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
            actor=Actor(**get_route_object().dict()),
            targets=[
                Target(old_target=get_route_object(), new_target=get_route_object())
            ],
            contexts=[
                Context(
                    app_name=AppName("app"),
                    namespace_name=NamespaceName("namespace"),
                    name=ContextName("context"),
                    displayname=ContextDisplayName("ctx"),
                )
            ],
            include_general_permissions=True,
            extra_request_data={"a": "b"},
        )
        result = await adapter_instance.to_policy_query(input_obj)
        assert result == GetPermissionsQuery(
            actor=PolicyObject(
                id="id",
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
                        id="id",
                        roles=[
                            PoliciesRole(
                                app_name="app", namespace_name="namespace", name="role"
                            )
                        ],
                        attributes={"a": "b"},
                    ),
                    new_target=PolicyObject(
                        id="id",
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
                id="id",
                roles=[
                    PoliciesRole(
                        app_name="app", namespace_name="namespace", name="role"
                    )
                ],
                attributes={"a": "b"},
            ),
            target_permissions=[
                TargetPermissions(
                    target_id="id",
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
            actor_id=ObjectIdentifier("id"),
            target_permissions=[
                PermissionResult(
                    target_id=ObjectIdentifier("id"),
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
