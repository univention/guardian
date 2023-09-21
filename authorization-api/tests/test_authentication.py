import guardian_lib.adapter_registry as adapter_registry
import pytest
import pytest_asyncio
from fastapi.routing import APIRoute
from guardian_authorization_api.main import app
from guardian_lib.ports import AuthenticationPort

pytest_plugins = "guardian_pytest.authentication"


@pytest_asyncio.fixture(scope="function")
async def oauth_authentication(auth_adapter_oauth):
    auth_adapter = await adapter_registry.ADAPTER_REGISTRY.request_port(
        AuthenticationPort
    )
    app.dependency_overrides[auth_adapter] = auth_adapter_oauth
    yield
    app.dependency_overrides = {}


def get_all_routes():
    routes = [route for route in app.routes if isinstance(route, APIRoute)]
    return [
        {"path": route.path, "method": method}
        for route in routes
        for method in route.methods
    ]


@pytest.mark.asyncio
async def test_all_routes_are_authenticated(client, oauth_authentication):
    for route in get_all_routes():
        #  Would like to have this parametrized, but client needs to be initialized first :(
        print(f"Testing: {route}")
        response = getattr(client, route["method"].lower())(
            route["path"].format(
                name="foo",
                app_name="bar",
                endpoint_name="myendpoint",
                namespace_name="univention",
            )
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}


class TestOauth:
    @pytest.mark.usefixtures("mock_get_jwk_set")
    def test_success(self, client, oauth_authentication, good_token):
        response = client.post(
            app.url_path_for("get_permissions"),
            json={"name": "test_app"},
            headers={"Authorization": f"Bearer {good_token}"},
        )
        assert response.status_code == 422  # TODO needs opa mock to get a 200

    @pytest.mark.usefixtures("mock_get_jwk_set")
    def test_bad_idp(self, client, oauth_authentication, bad_idp_token):
        response = client.post(
            app.url_path_for("get_permissions"),
            json={"name": "test_app"},
            headers={"Authorization": f"Bearer {bad_idp_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.usefixtures("mock_get_jwk_set")
    def test_expired_token(self, client, oauth_authentication, expired_token):
        response = client.post(
            app.url_path_for("get_permissions"),
            json={"name": "test_app"},
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.usefixtures("mock_get_jwk_set")
    def test_bad_audience_token(self, client, oauth_authentication, bad_audience_token):
        response = client.post(
            app.url_path_for("get_permissions"),
            json={"name": "test_app"},
            headers={"Authorization": f"Bearer {bad_audience_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.usefixtures("mock_get_jwk_set")
    def test_bad_signature_token(
        self, client, oauth_authentication, bad_signature_token
    ):
        response = client.post(
            app.url_path_for("get_permissions"),
            json={"name": "test_app"},
            headers={"Authorization": f"Bearer {bad_signature_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.usefixtures("mock_get_jwk_set")
    def test_wrong_key(self, client, oauth_authentication, wrong_key_token):
        response = client.post(
            app.url_path_for("get_permissions"),
            json={"name": "test_app"},
            headers={"Authorization": f"Bearer {wrong_key_token}"},
        )
        assert response.status_code == 401
