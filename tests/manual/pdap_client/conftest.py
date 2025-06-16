import pytest
import pytest_asyncio
from aiohttp import ClientSession
from pdap_access_manager import AccessManager

from src.pdap_api.client import PDAPClient
from src.util.helper_functions import get_from_env


@pytest_asyncio.fixture
async def client_session():
    async with ClientSession() as session:
        yield session

@pytest.fixture
def access_manager(client_session):
    return AccessManager(
        email=get_from_env("PDAP_PROD_EMAIL"),
        password=get_from_env("PDAP_PROD_PASSWORD"),
        api_key=get_from_env("PDAP_API_KEY", allow_none=True),
        session=client_session
    )

@pytest.fixture
def access_manager_dev(client_session):
    return AccessManager(
        email=get_from_env("PDAP_DEV_EMAIL"),
        password=get_from_env("PDAP_DEV_PASSWORD"),
        api_key=get_from_env("PDAP_DEV_API_KEY", allow_none=True),
        data_sources_url=get_from_env("PDAP_DEV_API_URL"),
        session=client_session
    )

@pytest.fixture
def pdap_client(access_manager):
    return PDAPClient(access_manager=access_manager)

@pytest.fixture
def pdap_client_dev(access_manager_dev):
    return PDAPClient(access_manager=access_manager_dev)