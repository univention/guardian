import pytest
from guardian_authorization_api.main import app


class TestAppEndpoints:
    @pytest.mark.asyncio
    async def test_post_permissions_401(self, client, error401):
        response = client.post(
            app.url_path_for("get_permissions"), json={"name": "test_app"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Not Authorized"}

    @pytest.mark.asyncio
    async def test_post_permissions_200(self, client):
        response = client.post(app.url_path_for("get_permissions"), json={"foo": "bar"})
        assert response.status_code == 422  # TODO needs opa mock to get a 200
