import pytest
from guardian_authorization_api.main import app


class TestAppEndpoints:
    @pytest.mark.asyncio
    @pytest.mark.usefixtures("client", "never_authorized")
    async def test_post_permissions_401(self, client):
        response = client.post(
            app.url_path_for("get_permissions"), json={"name": "test_app"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Not Authorized"}

    @pytest.mark.asyncio
    async def test_post_permissions_200(self, client):
        response = client.post(
            app.url_path_for("get_permissions"), json={"name": "test_app"}
        )
        assert response.status_code == 200
        assert response.json() == {"detail": "Not Authorized"}
