from unittest.mock import AsyncMock, Mock

import pytest
from guardian_management_api.adapters.authz import (
    AlwaysAuthorizedAdapter,
    GuardianAuthorizationAdapter,
    NeverAuthorizedAdapter,
    _get_resource_target,
)
from guardian_management_api.errors import AuthorizationError
from guardian_management_api.models.authz import (
    Actor,
    OperationType,
    Resource,
    ResourceType,
)
from httpx import Request, Response


class TestAlwaysAuthorizedAdapter:
    @pytest.mark.asyncio
    async def test_authorize_operation(self):
        adapter = AlwaysAuthorizedAdapter()
        assert await adapter.authorize_operation(
            Actor(id="test"),
            OperationType.READ_RESOURCE,
            [
                Resource(
                    app_name="app",
                    namespace_name="namespace",
                    name="resource",
                    resource_type=ResourceType.PERMISSION,
                )
            ],
        ) == {"app:namespace:resource": True}


class TestNeverAuthorizedAdapter:
    @pytest.mark.asyncio
    async def test_authorize_operation(self):
        adapter = NeverAuthorizedAdapter()
        assert await adapter.authorize_operation(
            Actor(id="test"),
            OperationType.READ_RESOURCE,
            [
                Resource(
                    app_name="app",
                    namespace_name="namespace",
                    name="resource",
                    resource_type=ResourceType.PERMISSION,
                )
            ],
        ) == {"app:namespace:resource": False}


class TestFunctions:
    @pytest.mark.parametrize(
        "resource,expected_result",
        [
            (
                Resource(
                    app_name="app",
                    namespace_name="namespace",
                    name="resource",
                    resource_type=ResourceType.PERMISSION,
                ),
                {
                    "app_name": "app",
                    "namespace_name": "namespace",
                    "name": "resource",
                },
            ),
            (
                Resource(
                    name="app",
                    resource_type=ResourceType.APP,
                ),
                {
                    "app_name": "app",
                    "name": "app",
                },
            ),
            (
                Resource(
                    name="namespace",
                    app_name="app",
                    resource_type=ResourceType.NAMESPACE,
                ),
                {
                    "app_name": "app",
                    "name": "namespace",
                },
            ),
            (
                Resource(
                    name="role",
                    namespace_name="namespace",
                    app_name="app",
                    resource_type=ResourceType.ROLE,
                ),
                {
                    "app_name": "app",
                    "namespace_name": "namespace",
                    "name": "role",
                },
            ),
            (
                Resource(
                    name="context",
                    namespace_name="namespace",
                    app_name="app",
                    resource_type=ResourceType.CONTEXT,
                ),
                {
                    "app_name": "app",
                    "namespace_name": "namespace",
                    "name": "context",
                },
            ),
            (
                Resource(
                    name="condition",
                    namespace_name="namespace",
                    app_name="app",
                    resource_type=ResourceType.CONDITION,
                ),
                {
                    "app_name": "app",
                    "namespace_name": "namespace",
                    "name": "condition",
                },
            ),
            (
                Resource(
                    name="capability",
                    namespace_name="namespace",
                    app_name="app",
                    resource_type=ResourceType.CAPABILITY,
                ),
                {
                    "app_name": "app",
                    "namespace_name": "namespace",
                    "name": "capability",
                },
            ),
        ],
    )
    def test_get_resource_target(self, resource, expected_result):
        assert _get_resource_target(resource) == expected_result

    @pytest.mark.parametrize(
        "resource",
        [
            Resource(
                name="role",
                resource_type=ResourceType.ROLE,
            ),
            Resource(
                name="context",
                resource_type=ResourceType.CONTEXT,
            ),
            Resource(
                name="condition",
                resource_type=ResourceType.CONDITION,
            ),
            Resource(
                name="capability",
                resource_type=ResourceType.CAPABILITY,
            ),
            Resource(
                name="capability",
                app_name="app",
                resource_type=ResourceType.CAPABILITY,
            ),
        ],
    )
    def test_get_resource_target_exception(self, resource):
        with pytest.raises(RuntimeError):
            _get_resource_target(resource)


class TestGuardianAuthorizationAdapter:
    @pytest.mark.asyncio
    async def test_authorize_operation_actor_not_allowed(self):
        adapter = GuardianAuthorizationAdapter()
        assert await adapter.authorize_operation(
            Actor(id="test"),
            OperationType.READ_RESOURCE,
            [
                Resource(
                    app_name="app",
                    namespace_name="namespace",
                    name="resource",
                    resource_type=ResourceType.PERMISSION,
                )
            ],
            client=Mock(
                fetch_token=AsyncMock(return_value="token"),
                post=AsyncMock(
                    return_value=Response(
                        200,
                        json={
                            "permissions_check_results": [
                                {
                                    "target_id": "app:namespace:resource",
                                    "actor_has_permissions": False,
                                }
                            ]
                        },
                        request=Request(
                            "GET", "https://guardian-authz-api/api/v1/authorize"
                        ),
                    )
                ),
            ),
        ) == {"app:namespace:resource": False}

    @pytest.mark.asyncio
    async def test_authorize_operation_actor_allowed(self):
        adapter = GuardianAuthorizationAdapter()
        assert await adapter.authorize_operation(
            Actor(id="test"),
            OperationType.READ_RESOURCE,
            [
                Resource(
                    app_name="app",
                    namespace_name="namespace",
                    name="resource",
                    resource_type=ResourceType.PERMISSION,
                )
            ],
            client=Mock(
                fetch_token=AsyncMock(return_value="token"),
                post=AsyncMock(
                    return_value=Response(
                        200,
                        json={
                            "permissions_check_results": [
                                {
                                    "target_id": "app:namespace:resource",
                                    "actor_has_permissions": True,
                                }
                            ]
                        },
                        request=Request(
                            "GET", "https://guardian-authz-api/api/v1/authorize"
                        ),
                    )
                ),
            ),
        ) == {"app:namespace:resource": True}

    @pytest.mark.asyncio
    async def test_authorize_operation_exception(self):
        adapter = GuardianAuthorizationAdapter()
        with pytest.raises(AuthorizationError) as exc:
            await adapter.authorize_operation(
                Actor(id="test"),
                OperationType.READ_RESOURCE,
                [
                    Resource(
                        app_name="app",
                        namespace_name="namespace",
                        name="resource",
                        resource_type=ResourceType.PERMISSION,
                    )
                ],
                client=Mock(
                    fetch_token=AsyncMock(return_value="token"),
                    post=AsyncMock(
                        return_value=Response(
                            400,
                            json={
                                "detail": "message",
                            },
                            request=Request(
                                "GET", "https://guardian-authz-api/api/v1/authorize"
                            ),
                        )
                    ),
                ),
            )

        assert (
            str(exc.value)
            == "Unsuccessful response from the Authorization API: {'detail': 'message'}"
        )


@pytest.mark.e2e
class TestGuardianAuthorizationAdapterIntegration:
    @pytest.mark.asyncio
    async def test_authorize_operation_actor_not_allowed_condition(self):
        adapter = GuardianAuthorizationAdapter()
        assert await adapter.authorize_operation(
            Actor(id="uid=guardian,cn=users,dc=school,dc=test"),
            OperationType.DELETE_RESOURCE,
            [
                Resource(
                    app_name="guardian",
                    namespace_name="builtin",
                    name="actor_does_not_have_role",
                    resource_type=ResourceType.CONDITION,
                )
            ],
        ) == {"guardian:builtin:actor_does_not_have_role": False}

    @pytest.mark.asyncio
    async def test_authorize_operation_actor_allowed_permission(self):
        adapter = GuardianAuthorizationAdapter()
        assert await adapter.authorize_operation(
            Actor(id="uid=guardian,cn=users,dc=school,dc=test"),
            OperationType.READ_RESOURCE,
            [
                Resource(
                    app_name="guardian",
                    namespace_name="management-api",
                    name="read_resource",
                    resource_type=ResourceType.PERMISSION,
                )
            ],
        ) == {"guardian:management-api:read_resource": True}

    @pytest.mark.asyncio
    async def test_authorize_operation_actor_not_allowed_app(self):
        adapter = GuardianAuthorizationAdapter()
        assert await adapter.authorize_operation(
            Actor(id="uid=guardian,cn=users,dc=school,dc=test"),
            OperationType.DELETE_RESOURCE,
            [
                Resource(
                    name="guardian",
                    resource_type=ResourceType.APP,
                )
            ],
        ) == {"guardian": False}

    @pytest.mark.asyncio
    async def test_authorize_operation_actor_allowed_app(self):
        adapter = GuardianAuthorizationAdapter()
        assert await adapter.authorize_operation(
            Actor(id="uid=guardian,cn=users,dc=school,dc=test"),
            OperationType.READ_RESOURCE,
            [
                Resource(
                    name="guardian",
                    resource_type=ResourceType.APP,
                )
            ],
        ) == {"guardian": True}
