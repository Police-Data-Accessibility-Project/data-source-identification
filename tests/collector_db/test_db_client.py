from collector_db.BatchInfo import BatchInfo
from collector_db.DTOs.DuplicateInfo import DuplicateInfo
from collector_db.DTOs.URLMapping import URLMapping
from collector_db.URLInfo import URLInfo
from core.enums import BatchStatus


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
    assert insert_urls_info.duplicates == [
        DuplicateInfo(
            source_url="https://example.com/1",
            original_url_id=1,
            duplicate_metadata={"name": "example_duplicate"},
            original_metadata={"name": "example_1"}
        )
    ]
