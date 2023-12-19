import os
from unittest.mock import AsyncMock, Mock, patch

import pytest
import requests
from guardian_lib.adapters.settings import EnvSettingsAdapter
from guardian_lib.ports import SettingsPort
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
from guardian_management_api.ports.authz import ResourceAuthorizationPort
from httpx import Request, Response
from port_loader import AsyncAdapterRegistry, AsyncAdapterSettingsProvider


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
                    "resource_type": "permission",
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
                    "resource_type": "app",
                    "app_name": "app",
                    "namespace_name": "",
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
                    "resource_type": "namespace",
                    "app_name": "app",
                    "namespace_name": "namespace",
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
                    "resource_type": "role",
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
                    "resource_type": "context",
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
                    "resource_type": "condition",
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
                    "resource_type": "capability",
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
    async def test_shutdown_on_config_error(self, monkeypatch):
        mock_get = Mock(side_effect=requests.exceptions.RequestException("test"))
        monkeypatch.setattr(requests, "get", mock_get)
        Settings = GuardianAuthorizationAdapter.get_settings_cls()
        settings = Settings(
            well_known_url="http://example.com",
            m2m_secret="secret",
            authorization_api_url="http://test",
        )
        with pytest.raises(RuntimeError) as exc:
            await GuardianAuthorizationAdapter().configure(settings)
            assert exc.value.code == 1

    @patch(
        "guardian_management_api.adapters.authz.get_oauth_settings",
        return_value={
            "mtls_endpoint_aliases": {
                "token_endpoint": "http://traefik/guardian/keycloak/realms/GuardianDev/protocol/openid-connect/token",
            },
            "jwks_uri": "http://traefik/guardian/keycloak/realms/GuardianDev/protocol/openid-connect/certs",
        },
    )
    @pytest.mark.asyncio
    async def test_configure(self, monkeypatch):
        registry = AsyncAdapterRegistry()
        registry.register_port(SettingsPort)
        registry.register_adapter(SettingsPort, adapter_cls=EnvSettingsAdapter)
        registry.set_adapter(SettingsPort, EnvSettingsAdapter)
        registry.set_adapter(SettingsPort, EnvSettingsAdapter)
        registry.register_adapter(
            AsyncAdapterSettingsProvider, adapter_cls=EnvSettingsAdapter
        )
        registry.set_adapter(AsyncAdapterSettingsProvider, EnvSettingsAdapter)
        registry.register_port(ResourceAuthorizationPort)
        registry.register_adapter(
            ResourceAuthorizationPort, adapter_cls=GuardianAuthorizationAdapter
        )
        with patch.dict(
            os.environ,
            {
                "OAUTH_ADAPTER__WELL_KNOWN_URL": "http://traefik/guardian/keycloak/realms/GuardianDev/.well-known/openid-configuration",
                "OAUTH_ADAPTER__M2M_SECRET": "univention",
                "GUARDIAN__MANAGEMENT__ADAPTER__AUTHORIZATION_API_URL": "http://test",
            },
        ):
            adapter = await registry.request_adapter(
                ResourceAuthorizationPort, GuardianAuthorizationAdapter
            )

        assert adapter.oauth_settings
        assert adapter.oauth_settings["mtls_endpoint_aliases"][
            "token_endpoint"
        ].endswith("/protocol/openid-connect/token")

    @patch("guardian_management_api.adapters.authz.AsyncOAuth2Client")
    @pytest.mark.asyncio
    async def test_authorize_operation_no_client_passed(self, client_patch):
        adapter = GuardianAuthorizationAdapter()
        adapter.oauth_settings = {
            "mtls_endpoint_aliases": {
                "token_endpoint": "http://test",
            }
        }
        adapter._settings = Mock()
        adapter._settings.m2m_secret = "secret"
        adapter._settings.authorization_api_url = "http://test"
        with pytest.raises(Exception):
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
                client=None,
            )
        client_patch.assert_called_once_with("guardian-management-api", "secret")

    @pytest.mark.asyncio
    async def test_authorize_operation_actor_not_allowed(self):
        adapter = GuardianAuthorizationAdapter()
        adapter.oauth_settings = {
            "mtls_endpoint_aliases": {
                "token_endpoint": "http://test",
            }
        }
        adapter._settings = Mock()
        adapter._settings.authorization_api_url = "http://test"
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
        adapter.oauth_settings = {
            "mtls_endpoint_aliases": {
                "token_endpoint": "http://test",
            }
        }
        adapter._settings = Mock()
        adapter._settings.authorization_api_url = "http://test"
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
        adapter.oauth_settings = {
            "mtls_endpoint_aliases": {
                "token_endpoint": "http://test",
            }
        }
        adapter._settings = Mock()
        adapter._settings.authorization_api_url = "http://test"
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
@pytest.mark.e2e_udm
class TestGuardianAuthorizationAdapterIntegration:
    @pytest.mark.asyncio
    async def test_authorize_operation_actor_not_allowed_condition(
        self, registry_test_adapters
    ):
        registry_test_adapters.register_adapter(
            ResourceAuthorizationPort, adapter_cls=GuardianAuthorizationAdapter
        )
        adapter = await registry_test_adapters.request_adapter(
            ResourceAuthorizationPort, GuardianAuthorizationAdapter
        )
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
    async def test_authorize_operation_actor_allowed_permission(
        self, registry_test_adapters
    ):
        registry_test_adapters.register_adapter(
            ResourceAuthorizationPort, adapter_cls=GuardianAuthorizationAdapter
        )
        adapter = await registry_test_adapters.request_adapter(
            ResourceAuthorizationPort, GuardianAuthorizationAdapter
        )
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
    async def test_authorize_operation_actor_not_allowed_app(
        self, registry_test_adapters
    ):
        registry_test_adapters.register_adapter(
            ResourceAuthorizationPort, adapter_cls=GuardianAuthorizationAdapter
        )
        adapter = await registry_test_adapters.request_adapter(
            ResourceAuthorizationPort, GuardianAuthorizationAdapter
        )
        assert await adapter.authorize_operation(
            Actor(id="uid=guardian,cn=users,dc=school,dc=test"),
            OperationType.DELETE_RESOURCE,
            [
                Resource(
                    name="other",
                    resource_type=ResourceType.APP,
                )
            ],
        ) == {"other": False}

    @pytest.mark.asyncio
    async def test_authorize_operation_actor_allowed_app(self, registry_test_adapters):
        registry_test_adapters.register_adapter(
            ResourceAuthorizationPort, adapter_cls=GuardianAuthorizationAdapter
        )
        adapter = await registry_test_adapters.request_adapter(
            ResourceAuthorizationPort, GuardianAuthorizationAdapter
        )
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
