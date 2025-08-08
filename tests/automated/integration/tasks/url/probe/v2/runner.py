from src.db.client.async_ import AsyncDatabaseClient
from tests.automated.integration.tasks.url.probe.setup.models.entry import TestURLProbeTaskEntry


class URLProbeTaskRunner:

    def __init__(self, adb_client: AsyncDatabaseClient):
        self.adb_client = adb_client

    async def run(self, entry: TestURLProbeTaskEntry):
        # Setup entry

        # Initialize Operator and Run Task

        # Check results