import pytest
from sqlalchemy import update, delete

from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import ChangeLogOperationType
from src.db.models.instantiations.change_log import ChangeLog
from src.db.models.instantiations.url.core.sqlalchemy import URL


class _TestChangeGetter:

    def __init__(self, adb: AsyncDatabaseClient):
        self.adb = adb

    async def get_change_log_entries(self):
        return await self.adb.get_all(ChangeLog)

@pytest.mark.asyncio
async def test_change_log(wiped_database, adb_client_test: AsyncDatabaseClient):
    getter = _TestChangeGetter(adb_client_test)

    # Confirm no entries in the change log table
    entries = await getter.get_change_log_entries()
    assert len(entries) == 0

    # Add entry to URL table
    url = URL(
        url="test_url",
        name="test_name",
        description="test_description",
        outcome='pending'
    )
    url_id = await adb_client_test.add(url, return_id=True)

    # Choose a single logged table -- URL -- for testing
    entries = await getter.get_change_log_entries()
    assert len(entries) == 1
    entry: ChangeLog = entries[0]
    assert entry.operation_type == ChangeLogOperationType.INSERT
    assert entry.table_name == "urls"
    assert entry.affected_id == url_id
    assert entry.old_data is None
    assert entry.new_data is not None
    nd = entry.new_data
    assert nd["id"] == url_id
    assert nd["url"] == "test_url"
    assert nd["name"] == "test_name"
    assert nd["description"] == "test_description"
    assert nd["outcome"] == "pending"
    assert nd["created_at"] is not None
    assert nd["updated_at"] is not None
    assert nd['record_type'] is None
    assert nd['collector_metadata'] is None

    # Update URL

    await adb_client_test.execute(
        update(URL).where(URL.id == url_id).values(
            name="new_name",
            description="new_description"
        )
    )

    # Confirm change log entry
    entries = await getter.get_change_log_entries()
    assert len(entries) == 2
    entry: ChangeLog = entries[1]
    assert entry.operation_type == ChangeLogOperationType.UPDATE
    assert entry.table_name == "urls"
    assert entry.affected_id == url_id
    assert entry.old_data is not None
    assert entry.new_data is not None
    od = entry.old_data
    nd = entry.new_data
    assert nd['description'] == "new_description"
    assert od['description'] == "test_description"
    assert nd['name'] == "new_name"
    assert od['name'] == "test_name"
    assert nd['updated_at'] is not None
    assert od['updated_at'] is not None

    # Delete URL
    await adb_client_test.execute(
        delete(URL).where(URL.id == url_id)
    )

    # Confirm change log entry
    entries = await getter.get_change_log_entries()
    assert len(entries) == 3
    entry: ChangeLog = entries[2]
    assert entry.operation_type == ChangeLogOperationType.DELETE
    assert entry.table_name == "urls"
    assert entry.affected_id == url_id
    assert entry.old_data is not None
    assert entry.new_data is None

