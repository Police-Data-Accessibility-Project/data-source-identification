from starlette.testclient import TestClient


def test_root_endpoint_without_mocked_dependency():
    # Here, we use the app without a dependency override
    from api.main import app
    with TestClient(app) as c:
        response = c.get(
            url="/",
            params={"test": "test"},
            headers={"Authorization": "Bearer token"}
        )

        # This should initially be denied by the security manager
        assert response.status_code == 401, response.text

        # Now, use a JWT obtained from the Data Sources App and succeed
        dotenv.load_dotenv()
        token = os.getenv("DS_APP_ACCESS_TOKEN")
        response = c.get(
            url="/",
            params={"test": "test"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200, response.text
