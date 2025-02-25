import jwt
import pytest
from starlette.testclient import TestClient

from api.main import app
from security_manager.SecurityManager import Permissions, ALGORITHM

PATCH_ROOT = "security_manager.SecurityManager"

def get_patch_path(patch_name):
    return f"{PATCH_ROOT}.{patch_name}"

@pytest.fixture
def mock_get_secret_key(mocker):
    mocker.patch(get_patch_path("get_secret_key"), return_value=SECRET_KEY)

SECRET_KEY = "test_secret_key"
VALID_TOKEN = "valid_token"
INVALID_TOKEN = "invalid_token"
FAKE_PAYLOAD = {
    "sub": 1,
    "permissions": [Permissions.SOURCE_COLLECTOR.value]
}

def test_api_with_valid_token(mock_get_secret_key):

    token = jwt.encode(FAKE_PAYLOAD, SECRET_KEY, algorithm=ALGORITHM)

    # Create Test Client
    with TestClient(app) as c:
        response = c.get(
            url="/",
            params={"test": "test"},
            headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200, response.text
