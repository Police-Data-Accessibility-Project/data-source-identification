import pytest

from src.core.tasks.url.operators.root_url.core import URLRootURLTaskOperator
from src.db.client.async_ import AsyncDatabaseClient


@pytest.fixture
def operator(adb_client_test: AsyncDatabaseClient) -> URLRootURLTaskOperator:
    return URLRootURLTaskOperator(adb_client=adb_client_test)