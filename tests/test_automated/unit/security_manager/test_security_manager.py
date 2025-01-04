import pytest
from unittest.mock import patch
from fastapi import HTTPException
from jwt import InvalidTokenError

from security_manager.SecurityManager import SecurityManager, Permissions, AccessInfo, get_access_info, ALGORITHM

SECRET_KEY = "test_secret_key"
VALID_TOKEN = "valid_token"
INVALID_TOKEN = "invalid_token"
FAKE_PAYLOAD = {"sub": 1, "permissions": [Permissions.SOURCE_COLLECTOR.value]}

PATCH_ROOT = "security_manager.SecurityManager"

def get_patch_path(patch_name):
    return f"{PATCH_ROOT}.{patch_name}"

@pytest.fixture
def mock_get_secret_key(mocker):
    mocker.patch(get_patch_path("get_secret_key"), return_value=SECRET_KEY)



@pytest.fixture
def mock_jwt_decode(mocker):
    mock_decode = mocker.patch(get_patch_path("jwt.decode"))
    def func(token, key, algorithms):
        if token == VALID_TOKEN:
            return FAKE_PAYLOAD
        raise InvalidTokenError
    mock_decode.side_effect = func
    return mock_decode


def test_validate_token_success(mock_get_secret_key, mock_jwt_decode):
    sm = SecurityManager()
    access_info = sm.validate_token(VALID_TOKEN)
    assert access_info.user_id == 1
    assert Permissions.SOURCE_COLLECTOR in access_info.permissions


def test_validate_token_failure(mock_get_secret_key, mock_jwt_decode):
    sm = SecurityManager()
    with pytest.raises(HTTPException) as exc_info:
        sm.validate_token(INVALID_TOKEN)
    assert exc_info.value.status_code == 401


def test_check_access_success(mock_get_secret_key, mock_jwt_decode):
    sm = SecurityManager()
    sm.check_access(VALID_TOKEN)  # Should not raise any exceptions.


def test_check_access_failure(mock_get_secret_key, mock_jwt_decode):
    # Modify payload to have insufficient permissions
    with patch(get_patch_path("SecurityManager.validate_token"), return_value=AccessInfo(user_id=1, permissions=[])):
        sm = SecurityManager()
        with pytest.raises(HTTPException) as exc_info:
            sm.check_access(VALID_TOKEN)
        assert exc_info.value.status_code == 403


def test_get_access_info(mock_get_secret_key, mock_jwt_decode):

    access_info = get_access_info(token=VALID_TOKEN)
    assert access_info.user_id == 1
    assert Permissions.SOURCE_COLLECTOR in access_info.permissions