from unittest.mock import MagicMock, AsyncMock

import pytest

from pdap_api_client.AccessManager import AccessManager
from pdap_api_client.PDAPClient import PDAPClient


@pytest.fixture
def mock_pdap_client() -> PDAPClient:
    mock_access_manager = MagicMock(
        spec=AccessManager
    )
    mock_access_manager.jwt_header = AsyncMock(
        return_value={"Authorization": "Bearer token"}
    )
    pdap_client = PDAPClient(
        access_manager=mock_access_manager
    )
    return pdap_client