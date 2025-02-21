from datetime import datetime, timedelta

import pytest

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DTOs.LogInfo import LogInfo
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.DTOs.URLMetadataInfo import URLMetadataInfo
from collector_db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource
from collector_manager.enums import URLStatus
from core.enums import BatchStatus, RecordType, SuggestionType
from tests.helpers.DBDataCreator import DBDataCreator


def test_insert_urls(db_client_test):
    # Insert batch
    batch_info = BatchInfo(
        strategy="ckan",
        status=BatchStatus.IN_PROCESS,
        parameters={},
        user_id=1
    )
    batch_id = db_client_test.insert_batch(batch_info)

    urls = [
        URLInfo(
            url="https://example.com/1",
            collector_metadata={"name": "example_1"},
        ),
        URLInfo(
            url="https://example.com/2",
        ),
        # Duplicate
        URLInfo(
            url="https://example.com/1",
            collector_metadata={"name": "example_duplicate"},
        )
    ]
    insert_urls_info = db_client_test.insert_urls(
        url_infos=urls,
        batch_id=batch_id
    )

    url_mappings = insert_urls_info.url_mappings
    assert len(url_mappings) == 2
    assert url_mappings[0].url == "https://example.com/1"
    assert url_mappings[1].url == "https://example.com/2"


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

def test_delete_old_logs(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()

    old_datetime = datetime.now() - timedelta(days=1)
    db_client = db_data_creator.db_client
    log_infos = []
    for i in range(3):
        log_infos.append(LogInfo(log="test log", batch_id=batch_id, created_at=old_datetime))
    db_client.insert_logs(log_infos=log_infos)
    logs = db_client.get_logs_by_batch_id(batch_id=batch_id)
    assert len(logs) == 3
    db_client.delete_old_logs()

    logs = db_client.get_logs_by_batch_id(batch_id=batch_id)
    assert len(logs) == 0

def test_delete_url_updated_at(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()
    url_id = db_data_creator.urls(batch_id=batch_id, url_count=1).url_mappings[0].url_id

    db_client = db_data_creator.db_client
    url_info = db_client.get_urls_by_batch(batch_id=batch_id, page=1)[0]

    old_updated_at = url_info.updated_at


    db_client.update_url(
        url_info=URLInfo(
            id=url_id,
            url="dg",
            collector_metadata={"test_metadata": "test_metadata"},
        )
    )

    url = db_client.get_urls_by_batch(batch_id=batch_id, page=1)[0]
    assert url.updated_at > old_updated_at

@pytest.mark.asyncio
async def test_get_url_metadata(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()
    url_id = db_data_creator.urls(batch_id=batch_id, url_count=1).url_mappings[0].url_id

    adb_client = AsyncDatabaseClient()

    await adb_client.add_url_metadata(
        url_metadata_info=URLMetadataInfo(
            url_id=url_id,
            attribute=URLMetadataAttributeType.RELEVANT,
            value="False",
            validation_status=ValidationStatus.PENDING_VALIDATION,
            validation_source=ValidationSource.MACHINE_LEARNING,
        )
    )

    metadata = await adb_client.get_url_metadata_by_status(url_status=URLStatus.PENDING)
    print(metadata)

@pytest.mark.asyncio
async def test_add_url_error_info(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()
    url_mappings = db_data_creator.urls(batch_id=batch_id, url_count=3).url_mappings
    url_ids = [url_mapping.url_id for url_mapping in url_mappings]

    adb_client = AsyncDatabaseClient()
    task_id = await db_data_creator.task()

    error_infos = []
    for url_mapping in url_mappings:
        uei = URLErrorPydanticInfo(
            url_id=url_mapping.url_id,
            error="test error",
            task_id=task_id
        )

        error_infos.append(uei)

    await adb_client.add_url_error_infos(
        url_error_infos=error_infos
    )

    results = await adb_client.get_urls_with_errors()

    assert len(results) == 3

    for result in results:
        assert result.url_id in url_ids
        assert result.error == "test error"

@pytest.mark.asyncio
async def test_get_urls_with_html_data_and_no_relevancy_metadata(
    db_data_creator: DBDataCreator,
):
    batch_id = db_data_creator.batch()
    url_mappings = db_data_creator.urls(batch_id=batch_id, url_count=3).url_mappings
    url_ids = [url_info.url_id for url_info in url_mappings]
    await db_data_creator.html_data(url_ids)
    await db_data_creator.metadata([url_ids[0]])
    results = await db_data_creator.adb_client.get_urls_with_html_data_and_without_metadata_type(
        without_metadata_type=URLMetadataAttributeType.RELEVANT
    )

    permitted_url_ids = [url_id for url_id in url_ids if url_id != url_ids[0]]
    assert len(results) == 2
    for result in results:
        assert result.url_id in permitted_url_ids
        assert len(result.html_infos) == 2

@pytest.mark.asyncio
async def test_get_urls_with_metadata(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()
    url_mappings = db_data_creator.urls(batch_id=batch_id, url_count=3).url_mappings
    url_ids = [url_info.url_id for url_info in url_mappings]
    await db_data_creator.metadata([url_ids[0]])
    # Neither of these two URLs should be picked up
    await db_data_creator.metadata([url_ids[1]], attribute=URLMetadataAttributeType.RECORD_TYPE)
    await db_data_creator.metadata([url_ids[2]], validation_status=ValidationStatus.VALIDATED)
    results = await db_data_creator.adb_client.get_urls_with_metadata(
        attribute=URLMetadataAttributeType.RELEVANT,
        validation_status=ValidationStatus.PENDING_VALIDATION
    )
    assert len(results) == 1

async def setup_for_get_next_url_for_final_review(
        db_data_creator: DBDataCreator,
        annotation_count: int,
        include_user_annotations: bool = True
):
    batch_id = db_data_creator.batch()
    url_mapping = db_data_creator.urls(batch_id=batch_id, url_count=1).url_mappings[0]
    await db_data_creator.html_data([url_mapping.url_id])

    async def add_metadata_annotation(count: int, value: str, metadata_id: int):
        for i in range(count):
            await db_data_creator.user_annotation(
                metadata_id=metadata_id,
                annotation=value
        )

    async def add_user_suggestion(count: int):
        agency_id = await db_data_creator.agency()
        for i in range(count):
            await db_data_creator.agency_user_suggestions(
                url_id=url_mapping.url_id,
                agency_id=agency_id
        )

    relevant_metadata_ids = await db_data_creator.metadata(
        url_ids=[url_mapping.url_id],
        attribute=URLMetadataAttributeType.RELEVANT,
        value="True",
        validation_source=ValidationSource.MACHINE_LEARNING,
        validation_status=ValidationStatus.PENDING_VALIDATION
    )
    relevant_metadata_id = relevant_metadata_ids[0]
    record_type_metadata_ids = await db_data_creator.metadata(
        url_ids=[url_mapping.url_id],
        attribute=URLMetadataAttributeType.RECORD_TYPE,
        value=RecordType.ARREST_RECORDS.value,
        validation_source=ValidationSource.MACHINE_LEARNING,
        validation_status=ValidationStatus.PENDING_VALIDATION
    )
    record_type_metadata_id = record_type_metadata_ids[0]

    if include_user_annotations:
        await add_metadata_annotation(annotation_count, "True", relevant_metadata_id)
        await add_metadata_annotation(1, "False", relevant_metadata_id)
        await add_metadata_annotation(3, RecordType.ARREST_RECORDS.value, record_type_metadata_id)
        await add_metadata_annotation(2, RecordType.DISPATCH_RECORDINGS.value, record_type_metadata_id)
        await add_metadata_annotation(1, RecordType.ACCIDENT_REPORTS.value, record_type_metadata_id)

    if include_user_annotations:
        # Add user suggestions for agencies, one suggested by 3 users, another by 2, another by 1
        for i in range(annotation_count):
            await add_user_suggestion(i + 1)


    return url_mapping


@pytest.mark.asyncio
async def test_get_next_url_for_final_review_basic(db_data_creator: DBDataCreator):
    """
    Test that an annotated URL is returned
    """

    url_mapping = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )

    await db_data_creator.agency_auto_suggestions(
        url_id=url_mapping.url_id,
        count=3
    )


    result = await db_data_creator.adb_client.get_next_url_for_final_review()

    assert result.url == url_mapping.url
    html_info = result.html_info
    assert html_info.description == "test description"
    assert html_info.title == "test html content"

    annotation_info = result.annotations
    relevant_info = annotation_info.relevant
    assert relevant_info.auto == True
    assert relevant_info.users.relevant == 3
    assert relevant_info.users.not_relevant == 1

    record_type_info = annotation_info.record_type
    assert record_type_info.auto == RecordType.ARREST_RECORDS
    user_d = record_type_info.users
    assert user_d[RecordType.ARREST_RECORDS] == 3
    assert user_d[RecordType.DISPATCH_RECORDINGS] == 2
    assert user_d[RecordType.ACCIDENT_REPORTS] == 1
    assert list(user_d.keys()) == [RecordType.ARREST_RECORDS, RecordType.DISPATCH_RECORDINGS, RecordType.ACCIDENT_REPORTS]


    agency_info = annotation_info.agency
    auto_agency_suggestions = agency_info.auto
    assert auto_agency_suggestions.unknown == False
    assert len(auto_agency_suggestions.suggestions) == 3

    # Check user agency suggestions exist and in descending order of count
    user_agency_suggestions = agency_info.users
    user_agency_suggestions_as_list = list(user_agency_suggestions.values())
    assert len(user_agency_suggestions_as_list) == 3
    for i in range(3):
        assert user_agency_suggestions_as_list[i].count == 3 - i



@pytest.mark.asyncio
async def test_get_next_url_for_final_review_favor_more_components(db_data_creator: DBDataCreator):
    """
    Test in the case of two URLs, favoring the one with more annotations for more components
    i.e., if one has annotations for record type and agency id, that should be favored over one with just record type
    """

    url_mapping_without_user_anno = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=False
    )

    url_mapping_with_user_anno = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )

    # Have both be listed as unknown

    for url_mapping in [url_mapping_with_user_anno, url_mapping_without_user_anno]:
        await db_data_creator.agency_auto_suggestions(
            url_id=url_mapping.url_id,
            count=3,
            suggestion_type=SuggestionType.UNKNOWN
        )

    result = await db_data_creator.adb_client.get_next_url_for_final_review()

    assert result.id == url_mapping_with_user_anno.url_id



@pytest.mark.asyncio
async def test_get_next_url_for_final_review_favor_more_annotations(db_data_creator: DBDataCreator):
    """
    Test in the case of two URLs with the same number of components annotated, favoring the one with more total annotations
    """
    url_mapping_lower_count = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=1,
        include_user_annotations=True
    )

    url_mapping_higher_count = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )

    for url_mapping in [url_mapping_lower_count, url_mapping_higher_count]:
        await db_data_creator.agency_confirmed_suggestion(
            url_id=url_mapping.url_id
        )

    result = await db_data_creator.adb_client.get_next_url_for_final_review()

    assert result.id == url_mapping_higher_count.url_id

    assert result.annotations.agency.confirmed is not None

    # TODO: Check that the the confirmed agency is shown for the result



@pytest.mark.asyncio
async def test_get_next_url_for_final_review_no_annotations(db_data_creator: DBDataCreator):
    """
    Test in the case of one URL with no annotations.
    Should be returned if it is the only one available.
    """
    batch_id = db_data_creator.batch()
    url_mapping = db_data_creator.urls(batch_id=batch_id, url_count=1).url_mappings[0]

    result = await db_data_creator.adb_client.get_next_url_for_final_review()

    assert result.id == url_mapping.url_id

    annotations = result.annotations

    agency = annotations.agency
    assert agency.confirmed is None
    assert agency.auto.unknown is True
    assert agency.auto.suggestions == []

    record_type = annotations.record_type
    assert record_type.auto is None
    assert record_type.users == {}

    relevant = annotations.relevant
    assert relevant.auto is None
    assert relevant.users.relevant == 0
    assert relevant.users.not_relevant == 0


async def test_get_next_url_for_final_review_only_confirmed_urls(db_data_creator: DBDataCreator):
    """
    Test in the case of one URL that is confirmed
    Should not be returned.
    """
    batch_id = db_data_creator.batch()