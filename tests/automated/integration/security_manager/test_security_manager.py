import jwt
import pytest
from starlette.testclient import TestClient

from src.api.main import app
from src.security.constants import ALGORITHM
from src.security.enums import Permissions


SECRET_KEY = "test_secret_key"
VALID_TOKEN = "valid_token"
INVALID_TOKEN = "invalid_token"
FAKE_PAYLOAD = {
    "sub": "1",
    "permissions": [Permissions.SOURCE_COLLECTOR.value]
}

def test_api_with_valid_token(
        monkeypatch
):

    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://discord.com")
    monkeypatch.setenv("DS_APP_SECRET_KEY", SECRET_KEY)
    token = jwt.encode(FAKE_PAYLOAD, SECRET_KEY, algorithm=ALGORITHM)

    # Create Test Client
    with TestClient(app) as c:
        response = c.get(
            url="/",
            params={"test": "test"},
            headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200, response.text
