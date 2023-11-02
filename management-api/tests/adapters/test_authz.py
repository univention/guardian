from unittest.mock import AsyncMock, Mock

import pytest
from guardian_management_api.adapters.authz import (
    AlwaysAuthorizedAdapter,
    GuardianAUthorizationAdapter,
    NeverAuthorizedAdapter,
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


class TestGuardianAUthorizationAdapter:
    @pytest.mark.asyncio
    async def test_authorize_operation_actor_not_allowed(self):
        adapter = GuardianAUthorizationAdapter()
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
                get=AsyncMock(
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
        adapter = GuardianAUthorizationAdapter()
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
                get=AsyncMock(
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
        adapter = GuardianAUthorizationAdapter()
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
                    get=AsyncMock(
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
