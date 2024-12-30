import pytest

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DTOs.DuplicateInfo import DuplicateInfo
from collector_db.DTOs.LogInfo import LogInfo
from collector_db.DTOs.URLMapping import URLMapping
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.DatabaseClient import DatabaseClient
from collector_db.models import Batch
from core.enums import BatchStatus
from tests.helpers.DBDataCreator import DBDataCreator


@pytest.mark.asyncio
async def test_insert_batch(db_client_test):
    client = db_client_test

    # Create a BatchInfo object with sample data
    batch_info = BatchInfo(
        strategy="Test Strategy",
        status=BatchStatus.IN_PROCESS,
        parameters={"key": "value"},
        total_url_count=100,
        original_url_count=80,
        duplicate_url_count=20,
        compute_time=10.5,
        strategy_success_rate=0.8,
        metadata_success_rate=0.9,
        agency_match_rate=0.7,
        record_type_match_rate=0.85,
        record_category_match_rate=0.75,
    )

    # Act: Insert the batch into the database
    batch_id = await client.insert_batch(batch_info=batch_info)

    # Assert: Check if the batch was inserted correctly
    async with client.session_maker() as session:
        batch = await session.get(Batch, batch_id)
        assert batch is not None
        assert batch.strategy == "Test Strategy"
        assert batch.status == BatchStatus.IN_PROCESS.value
        assert batch.parameters == {"key": "value"}
        assert batch.total_url_count == 100
        assert batch.original_url_count == 80
        assert batch.duplicate_url_count == 20
        assert batch.compute_time == 10.5
        assert batch.strategy_success_rate == 0.8
        assert batch.metadata_success_rate == 0.9
        assert batch.agency_match_rate == 0.7
        assert batch.record_type_match_rate == 0.85
        assert batch.record_category_match_rate == 0.75


def test_insert_urls(db_client_test):
    # Insert batch
    batch_info = BatchInfo(
        strategy="ckan",
        status=BatchStatus.IN_PROCESS,
        parameters={}
    )
    batch_id = db_client_test.insert_batch(batch_info)

    urls = [
        URLInfo(
            url="https://example.com/1",
            url_metadata={"name": "example_1"},
        ),
        URLInfo(
            url="https://example.com/2",
        ),
        # Duplicate
        URLInfo(
            url="https://example.com/1",
            url_metadata={"name": "example_duplicate"},
        )
    ]
    insert_urls_info = db_client_test.insert_urls(
        url_infos=urls,
        batch_id=batch_id
    )

    assert insert_urls_info.url_mappings == [
        URLMapping(
            url="https://example.com/1",
            url_id=1
        ),
        URLMapping(
            url="https://example.com/2",
            url_id=2
        )
    ]
    assert insert_urls_info.original_count == 2
    assert insert_urls_info.duplicate_count == 1


def test_insert_logs(db_data_creator: DBDataCreator):
    batch_id_1 = db_data_creator.batch()
    batch_id_2 = db_data_creator.batch()

    db_client = db_data_creator.db_client
    db_client.insert_logs(
        log_infos=[
            LogInfo(log="test log", batch_id=batch_id_1),
            LogInfo(log="test log", batch_id=batch_id_1),
            LogInfo(log="test log", batch_id=batch_id_2),
        ]
    )

    logs = db_client.get_logs_by_batch_id(batch_id_1)
    assert len(logs) == 2

    logs = db_client.get_logs_by_batch_id(batch_id_2)
    assert len(logs) == 1


