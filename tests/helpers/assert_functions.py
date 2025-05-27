from db.AsyncDatabaseClient import AsyncDatabaseClient
from db.models import Task


async def assert_database_has_no_tasks(adb_client: AsyncDatabaseClient):
    tasks = await adb_client.get_all(Task)
    assert len(tasks) == 0