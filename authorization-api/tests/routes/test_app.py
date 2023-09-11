from guardian_authorization_api.main import app


class TestAppEndpoints:
    def test_post_permissions(self, client):
        response = client.post(
            app.url_path_for("get_permissions"), json={"name": "test_app"}
        )
        assert response.status_code == 200
        assert response.json() == {
            "app": {
                "display_name": None,
                "name": "test_app",
                "resource_url": "apps/test_app",
            }
        }
