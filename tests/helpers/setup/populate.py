from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.instantiations.url.core import URL


async def populate_database(adb_client: AsyncDatabaseClient) -> None:
    """Populate database with test data."""
    url = URL(
        url="https://www.test-data.com/static-test-data",
        name="Fake test data",
        description="Test data populated as a result of `reset_database`, "
                    "which imitates a validated URL synchronized from the Data Sources App.",
        collector_metadata={
            "source_collector": "test-data",
        },
        outcome='validated',
        record_type="Other"
    )
    await adb_client.add(url)