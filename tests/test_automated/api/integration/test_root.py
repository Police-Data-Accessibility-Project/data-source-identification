import os

import dotenv
from starlette.testclient import TestClient


def test_read_main(api_test_helper):

    data = api_test_helper.request_validator.get(url="/?test=test")
    assert data == {"message": "Hello World"}


def test_root_endpoint_with_mocked_dependency(client):
    response = client.get(
        url="/",
        params={"test": "test"},
        headers={"Authorization": "Bearer token"}
    )

    assert response.status_code == 200, response.text
    assert response.json() == {"message": "Hello World"}, response.text

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


