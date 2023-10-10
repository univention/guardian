import pytest
from guardian_management_api.adapters.authz import (
    AlwaysAuthorizedAdapter,
    NeverAuthorizedAdapter,
)
from guardian_management_api.models.authz import (
    Actor,
    OperationType,
    Resource,
    ResourceType,
)


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
