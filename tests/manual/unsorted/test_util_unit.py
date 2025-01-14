import pytest
from unittest.mock import patch
from util.huggingface_api_manager import HuggingfaceInterface
import huggingface_hub

def test_init_success():
    with patch.object(huggingface_hub, 'login') as login_mock, \
            patch.object(huggingface_hub, 'HfApi') as api_mock:
        manager = HuggingfaceInterface('testing-access-token', 'repo')
        login_mock.assert_called_once_with(token='testing-access-token')
        api_mock.assert_called_once_with()
        assert manager.repo_id == 'repo'


def test_init_empty_access_token():
    with pytest.raises(ValueError, match="Access token cannot be empty."):
        HuggingfaceInterface('', 'repo')


def test_init_no_access_token():
    with pytest.raises(ValueError, match="Access token cannot be empty."):
        HuggingfaceInterface(None, 'repo')