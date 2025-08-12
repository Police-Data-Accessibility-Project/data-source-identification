import pytest

from src.db.models.impl.log.pydantic.info import LogInfo
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_insert_logs(db_data_creator: DBDataCreator):
    batch_id_1 = db_data_creator.batch()
    batch_id_2 = db_data_creator.batch()

    adb_client = db_data_creator.adb_client
    db_client = db_data_creator.db_client
    db_client.insert_logs(
        log_infos=[
            LogInfo(log="test log", batch_id=batch_id_1),
            LogInfo(log="test log", batch_id=batch_id_1),
            LogInfo(log="test log", batch_id=batch_id_2),
        ]
    )

    logs = await adb_client.get_logs_by_batch_id(batch_id_1)
    assert len(logs) == 2

    logs = await adb_client.get_logs_by_batch_id(batch_id_2)
    assert len(logs) == 1
