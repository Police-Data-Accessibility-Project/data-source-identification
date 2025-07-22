from typing import Optional

import pytest

from src.core.tasks.url.operators.url_miscellaneous_metadata.core import URLMiscellaneousMetadataTaskOperator
from src.db.models.instantiations.url.optional_data_source_metadata import URLOptionalDataSourceMetadata
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.collectors.enums import CollectorType
from src.core.tasks.url.enums import TaskOperatorOutcome
from tests.helpers.db_data_creator import DBDataCreator


def batch_and_url(
    db_data_creator: DBDataCreator,
    collector_type: CollectorType,
    collector_metadata: Optional[dict]
):
    batch_id = db_data_creator.batch(strategy=collector_type)
    url_id = db_data_creator.urls(
        batch_id=batch_id,
        url_count=1,
        collector_metadata=collector_metadata
    ).url_mappings[0].url_id
    return url_id


@pytest.mark.asyncio
async def test_url_miscellaneous_metadata_task(db_data_creator: DBDataCreator):

    operator = URLMiscellaneousMetadataTaskOperator(adb_client=db_data_creator.adb_client)

    # Currently, task should not meet prerequisites
    meets_prereqs = await operator.meets_task_prerequisites()
    assert not meets_prereqs

    # Add one URL for each of the following batches, with appropriate collector metadata:
    # ckan
    ckan_url_id = batch_and_url(
        db_data_creator,
        CollectorType.CKAN,
        collector_metadata={
            "submitted_name": "Test CKAN Name",
            "description": "Test CKAN Description",
            "record_format": ["CSV", "JSON"],
            "data_portal_type": "Test Data Portal Type",
            "supplying_entity": "Test Supplying Entity"
        }
    )
    # muckrock_simple
    muckrock_simple_url_id = batch_and_url(
        db_data_creator,
        CollectorType.MUCKROCK_SIMPLE_SEARCH,
        collector_metadata={
            'title': 'Test Muckrock Simple Title',
        }
    )
    # muckrock_county
    muckrock_county_url_id = batch_and_url(
        db_data_creator,
        CollectorType.MUCKROCK_COUNTY_SEARCH,
        collector_metadata={
            'title': 'Test Muckrock County Title',
        }
    )
    # muckrock_all
    muckrock_all_url_id = batch_and_url(
        db_data_creator,
        CollectorType.MUCKROCK_ALL_SEARCH,
        collector_metadata={
            'title': 'Test Muckrock All Title',
        }
    )
    # auto_googler
    auto_googler_url_id = batch_and_url(
        db_data_creator,
        CollectorType.AUTO_GOOGLER,
        collector_metadata={
            "title" : "Test Auto Googler Title",
            "snippet" : "Test Auto Googler Snippet"
        }
    )
    # common_crawler
    common_crawler_url_id = batch_and_url(
        db_data_creator,
        CollectorType.COMMON_CRAWLER,
        collector_metadata=None
    )
    # Add URL HTML
    await db_data_creator.html_data([common_crawler_url_id])
    # example

    # Check that task now meets prerequisites
    meets_prereqs = await operator.meets_task_prerequisites()
    assert meets_prereqs

    # Run task
    run_info = await operator.run_task(1)
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS

    # Check that each URL has the expected name/description and optional metadata
    expected_urls = {
        common_crawler_url_id: ("test html content", "test description"),
        auto_googler_url_id: ("Test Auto Googler Title", "Test Auto Googler Snippet"),
        ckan_url_id: ("Test CKAN Name", "Test CKAN Description"),
        muckrock_simple_url_id: ("Test Muckrock Simple Title", "Test Muckrock Simple Title"),
        muckrock_county_url_id: ("Test Muckrock County Title", "Test Muckrock County Title"),
        muckrock_all_url_id: ("Test Muckrock All Title", "Test Muckrock All Title"),
    }

    urls: list[URL] = await db_data_creator.adb_client.get_all(URL)
    assert len(urls) == len(expected_urls)

    seen_ids = set()

    for url in urls:
        assert url.id not in seen_ids, f"Duplicate url.id found: {url.id}"
        seen_ids.add(url.id)

        assert url.id in expected_urls, f"Unexpected url.id: {url.id}"
        expected_name, expected_description = expected_urls[url.id]
        assert url.name == expected_name, f"For url.id {url.id}, expected name {expected_name}, got {url.name}"
        assert url.description == expected_description, f"For url.id {url.id}, expected description {expected_description}, got {url.description}"

    expected_urls = {
        common_crawler_url_id: (None, None, None),
        auto_googler_url_id: (None, None, None),
        ckan_url_id: (["CSV", "JSON"], "Test Data Portal Type", "Test Supplying Entity"),
        muckrock_simple_url_id: (None, None, None),
        muckrock_county_url_id: (None, None, None),
        muckrock_all_url_id: (None, None, None),
    }

    metadatas: list[URLOptionalDataSourceMetadata] = await db_data_creator.adb_client.get_all(URLOptionalDataSourceMetadata)
    seen_ids = set()
    for metadata in metadatas:
        assert metadata.url_id not in seen_ids, f"Duplicate url.id found: {metadata.url_id}"
        seen_ids.add(metadata.url_id)

        assert metadata.url_id in expected_urls, f"Unexpected url.id: {metadata.url_id}"
        expected_record_format, expected_data_portal_type, expected_supplying_entity = expected_urls[metadata.url_id]
        assert metadata.record_formats == expected_record_format, f"For url.id {metadata.url_id}, expected record_format {expected_record_format}, got {metadata.url_id}"
        assert metadata.data_portal_type == expected_data_portal_type, f"For url.id {metadata.url_id}, expected data_portal_type {expected_data_portal_type}, got {metadata.url_id}"
        assert metadata.supplying_entity == expected_supplying_entity, f"For url.id {metadata.url_id}, expected supplying_entity {expected_supplying_entity}, got {metadata.url_id}"



