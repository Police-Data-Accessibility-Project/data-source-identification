from datetime import datetime, timedelta

import pytest

from src.db.dtos.log import LogInfo
from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_delete_old_logs(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()

    old_datetime = datetime.now() - timedelta(days=7)
    db_client = db_data_creator.db_client
    adb_client = db_data_creator.adb_client
    log_infos = []
    for i in range(3):
        log_infos.append(LogInfo(log="test log", batch_id=batch_id, created_at=old_datetime))
    db_client.insert_logs(log_infos=log_infos)
    logs = await adb_client.get_logs_by_batch_id(batch_id=batch_id)
    assert len(logs) == 3
    await adb_client.delete_old_logs()

    logs = await adb_client.get_logs_by_batch_id(batch_id=batch_id)
    assert len(logs) == 0
