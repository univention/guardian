import pytest
from guardian_management_api.models.authz import Resource, ResourceType


class TestResource:
    @pytest.mark.parametrize(
        "resource,expected",
        [
            (
                Resource(
                    resource_type=ResourceType.APP,
                    app_name=None,
                    namespace_name=None,
                    name="app",
                ),
                "app",
            ),
            (
                Resource(
                    resource_type=ResourceType.APP,
                    app_name=None,
                    namespace_name="foo",
                    name="app",
                ),
                "app",
            ),
            (
                Resource(
                    resource_type=ResourceType.NAMESPACE,
                    app_name=None,
                    namespace_name=None,
                    name="namespace",
                ),
                "None:namespace",
            ),
            (
                Resource(
                    resource_type=ResourceType.NAMESPACE,
                    app_name="app",
                    namespace_name=None,
                    name="namespace",
                ),
                "app:namespace",
            ),
            (
                Resource(
                    resource_type=ResourceType.PERMISSION,
                    app_name="app",
                    namespace_name="namespace",
                    name="name",
                ),
                "app:namespace:name",
            ),
            (
                Resource(
                    resource_type=ResourceType.CAPABILITY,
                    app_name="app",
                    namespace_name="namespace",
                    name="name",
                ),
                "app:namespace:name",
            ),
        ],
    )
    def test_id_property(self, resource, expected):
        assert resource.id == expected
