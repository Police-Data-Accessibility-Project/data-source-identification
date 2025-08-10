import pytest

from src.db.client.async_ import AsyncDatabaseClient
from tests.automated.integration.tasks.url.impl.probe.check.manager import TestURLProbeCheckManager
from tests.automated.integration.tasks.url.impl.probe.setup.manager import TestURLProbeSetupManager


@pytest.fixture
def setup_manager(
    adb_client_test: AsyncDatabaseClient
) -> TestURLProbeSetupManager:
    return TestURLProbeSetupManager(
        adb_client=adb_client_test
    )


@pytest.fixture
def check_manager(
    adb_client_test: AsyncDatabaseClient
) -> TestURLProbeCheckManager:
    return TestURLProbeCheckManager(
        adb_client=adb_client_test
    )