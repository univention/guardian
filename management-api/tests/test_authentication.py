import os

import guardian_lib.adapter_registry as adapter_registry
import pytest
import pytest_asyncio
import requests
from fastapi.routing import APIRoute
from guardian_lib.adapters.authentication import FastAPIOAuth2, get_oauth_settings
from guardian_lib.ports import AuthenticationPort
from guardian_management_api.main import app

pytest_plugins = "guardian_pytest.authentication"


@pytest_asyncio.fixture(scope="function")
async def oauth_authentication_mock(auth_adapter_oauth):
    auth_adapter = await adapter_registry.ADAPTER_REGISTRY.request_port(
        AuthenticationPort
    )
    app.dependency_overrides[auth_adapter] = auth_adapter_oauth
    yield
    app.dependency_overrides = {}


@pytest_asyncio.fixture(scope="function")
async def oauth_authentication_keycloak():
    auth_adapter = await adapter_registry.ADAPTER_REGISTRY.request_port(
        AuthenticationPort
    )
    app.dependency_overrides[auth_adapter] = FastAPIOAuth2
    yield
    app.dependency_overrides = {}


def get_all_routes():
    routes = [route for route in app.routes if isinstance(route, APIRoute)]
    return [
        {"path": route.path, "method": method}
        for route in routes
        for method in route.methods
    ]


@pytest.mark.usefixtures("create_tables")
@pytest.mark.asyncio
async def test_all_routes_are_authenticated(client, oauth_authentication_mock):
    for route in get_all_routes():
        #  Would like to have this parametrized, but client needs to be initialized first :(
        print(f"Testing: {route}")
        response = getattr(client, route["method"].lower())(
            route["path"].format(
                name="foo", app_name="bar", namespace_name="univention"
            )
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}


class TestOauth:
    @pytest.mark.usefixtures("create_tables", "mock_get_jwk_set")
    def test_success(self, client, oauth_authentication_mock, good_token):
        response = client.post(
            app.url_path_for("create_app"),
            json={"name": "test_app"},
            headers={"Authorization": f"Bearer {good_token}"},
        )
        assert response.status_code == 201

    @pytest.mark.usefixtures("create_tables", "mock_get_jwk_set")
    def test_bad_idp(self, client, oauth_authentication_mock, bad_idp_token):
        response = client.post(
            app.url_path_for("create_app"),
            json={"name": "test_app"},
            headers={"Authorization": f"Bearer {bad_idp_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.usefixtures("create_tables", "mock_get_jwk_set")
    def test_expired_token(self, client, oauth_authentication_mock, expired_token):
        response = client.post(
            app.url_path_for("create_app"),
            json={"name": "test_app"},
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.usefixtures("create_tables", "mock_get_jwk_set")
    def test_bad_audience_token(
        self, client, oauth_authentication_mock, bad_audience_token
    ):
        response = client.post(
            app.url_path_for("create_app"),
            json={"name": "test_app"},
            headers={"Authorization": f"Bearer {bad_audience_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.usefixtures("create_tables", "mock_get_jwk_set")
    def test_bad_signature_token(
        self, client, oauth_authentication_mock, bad_signature_token
    ):
        response = client.post(
            app.url_path_for("create_app"),
            json={"name": "test_app"},
            headers={"Authorization": f"Bearer {bad_signature_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.usefixtures("create_tables", "mock_get_jwk_set")
    def test_wrong_key(self, client, oauth_authentication_mock, wrong_key_token):
        response = client.post(
            app.url_path_for("create_app"),
            json={"name": "test_app"},
            headers={"Authorization": f"Bearer {wrong_key_token}"},
        )
        assert response.status_code == 401


@pytest.fixture
@pytest.mark.asyncio
async def get_keycloak_token():
    oauth_settings = await get_oauth_settings(
        os.getenv("OAUTH_ADAPTER__WELL_KNOWN_URL")
    )
    response = requests.post(
        oauth_settings["token_endpoint"],
        data={
            "grant_type": "password",
            "username": "guardian",
            "password": "univention",
            "client_id": "guardian-cli",
        },
        verify=os.environ.get("SSL_CERT_FILE", False),
    )
    token = response.json()["access_token"]
    return token


@pytest.mark.e2e
@pytest.mark.e2e_udm
class TestAuthenticationIntegration:
    def test_get_app_not_allowed(
        self, create_tables, oauth_authentication_mock, client
    ):
        response = client.get(app.url_path_for("get_app", name="guardian"))
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_app_allowed_keycloak(
        self,
        create_tables,
        sqlalchemy_mixin,
        create_app,
        oauth_authentication_keycloak,
        client,
        get_keycloak_token,
    ):
        async with sqlalchemy_mixin.session() as session:
            await create_app(session, "guardian", display_name=None)
        token = await get_keycloak_token

        response = client.get(
            app.url_path_for("get_app", name="guardian"),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
