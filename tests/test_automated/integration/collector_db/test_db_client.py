from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DTOs.LogInfo import LogInfo
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.DTOs.URLMapping import URLMapping
from collector_db.constants import PLACEHOLDER_AGENCY_NAME
from collector_db.models import URL, ReviewingUserURL, URLOptionalDataSourceMetadata, ConfirmedURLAgency, Agency
from collector_manager.enums import URLStatus
from core.DTOs.FinalReviewApprovalInfo import FinalReviewApprovalInfo
from core.enums import BatchStatus, RecordType, SuggestionType
from tests.helpers.complex_test_data_functions import setup_for_get_next_url_for_annotation, setup_for_annotate_agency
from tests.helpers.DBDataCreator import DBDataCreator
from tests.helpers.complex_test_data_functions import setup_for_get_next_url_for_final_review

@pytest.mark.asyncio
async def test_insert_urls(
        db_client_test,
        adb_client_test
):
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
    insert_urls_info = await adb_client_test.insert_urls(
        url_infos=urls,
        batch_id=batch_id
    )

    url_mappings = insert_urls_info.url_mappings
    assert len(url_mappings) == 2
    assert url_mappings[0].url == "https://example.com/1"
    assert url_mappings[1].url == "https://example.com/2"


    assert insert_urls_info.original_count == 2
    assert insert_urls_info.duplicate_count == 1

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

@pytest.mark.asyncio
async def test_delete_old_logs(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()

    old_datetime = datetime.now() - timedelta(days=1)
    db_client = db_data_creator.db_client
    adb_client = db_data_creator.adb_client
    log_infos = []
    for i in range(3):
        log_infos.append(LogInfo(log="test log", batch_id=batch_id, created_at=old_datetime))
    db_client.insert_logs(log_infos=log_infos)
    logs = await adb_client.get_logs_by_batch_id(batch_id=batch_id)
    assert len(logs) == 3
    db_client.delete_old_logs()

    logs = await adb_client.get_logs_by_batch_id(batch_id=batch_id)
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
async def test_get_next_url_for_final_review_basic(db_data_creator: DBDataCreator):
    """
    Test that an annotated URL is returned
    """

    setup_info = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )

    url_mapping = setup_info.url_mapping

    await db_data_creator.agency_auto_suggestions(
        url_id=url_mapping.url_id,
        count=3
    )


    result = await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=None
    )

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
async def test_get_next_url_for_final_review_batch_id_filtering(db_data_creator: DBDataCreator):
    setup_info_1 = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )

    setup_info_2 = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )

    url_mapping_1 = setup_info_1.url_mapping
    url_mapping_2 = setup_info_2.url_mapping

    # If a batch id is provided, return first valid URL with that batch id
    result_with_batch_id =await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=setup_info_2.batch_id
    )

    assert result_with_batch_id.url == url_mapping_2.url

    # If no batch id is provided, return first valid URL
    result_no_batch_id =await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=None
    )

    assert result_no_batch_id.url == url_mapping_1.url


@pytest.mark.asyncio
async def test_get_next_url_for_final_review_favor_more_components(db_data_creator: DBDataCreator):
    """
    Test in the case of two URLs, favoring the one with more annotations for more components
    i.e., if one has annotations for record type and agency id, that should be favored over one with just record type
    """

    setup_info_without_user_anno = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=False
    )
    url_mapping_without_user_anno = setup_info_without_user_anno.url_mapping

    setup_info_with_user_anno = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )
    url_mapping_with_user_anno = setup_info_with_user_anno.url_mapping

    # Have both be listed as unknown

    for url_mapping in [url_mapping_with_user_anno, url_mapping_without_user_anno]:
        await db_data_creator.agency_auto_suggestions(
            url_id=url_mapping.url_id,
            count=3,
            suggestion_type=SuggestionType.UNKNOWN
        )

    result = await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=None
    )

    assert result.id == url_mapping_with_user_anno.url_id



@pytest.mark.asyncio
async def test_get_next_url_for_final_review_favor_more_annotations(
        db_data_creator: DBDataCreator,
        wipe_database
):
    """
    Test in the case of two URLs with the same number of components annotated, favoring the one with more total annotations
    """
    setup_info_lower_count = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=1,
        include_user_annotations=True
    )
    url_mapping_lower_count = setup_info_lower_count.url_mapping

    setup_info_higher_count = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )
    url_mapping_higher_count = setup_info_higher_count.url_mapping

    for url_mapping in [url_mapping_lower_count, url_mapping_higher_count]:
        await db_data_creator.agency_confirmed_suggestion(
            url_id=url_mapping.url_id
        )

    result = await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=None
    )

    assert result.id == url_mapping_higher_count.url_id

    assert result.annotations.agency.confirmed is not None




@pytest.mark.asyncio
async def test_get_next_url_for_final_review_no_annotations(db_data_creator: DBDataCreator):
    """
    Test in the case of one URL with no annotations.
    Should be returned if it is the only one available.
    """
    batch_id = db_data_creator.batch()
    url_mapping = db_data_creator.urls(batch_id=batch_id, url_count=1).url_mappings[0]

    result = await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=None
    )

    assert result.id == url_mapping.url_id

    annotations = result.annotations

    agency = annotations.agency
    assert agency.confirmed == []
    assert agency.auto.unknown is True
    assert agency.auto.suggestions == []

    record_type = annotations.record_type
    assert record_type.auto is None
    assert record_type.users == {}

    relevant = annotations.relevant
    assert relevant.auto is None
    assert relevant.users.relevant == 0
    assert relevant.users.not_relevant == 0

@pytest.mark.asyncio
async def test_get_next_url_for_final_review_only_confirmed_urls(db_data_creator: DBDataCreator):
    """
    Test in the case of one URL that is submitted
    Should not be returned.
    """
    batch_id = db_data_creator.batch()
    url_mapping = db_data_creator.urls(
        batch_id=batch_id,
        url_count=1,
        outcome=URLStatus.SUBMITTED
    ).url_mappings[0]

    result = await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=None
    )

    assert result is None

@pytest.mark.asyncio
async def test_approve_url_basic(db_data_creator: DBDataCreator):
    setup_info = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )
    url_mapping = setup_info.url_mapping

    # Add confirmed agency
    agency_id = await db_data_creator.agency_confirmed_suggestion(
        url_id=url_mapping.url_id
    )

    adb_client = db_data_creator.adb_client
    # Approve URL. Only URL should be affected. No other properties should be changed.
    await adb_client.approve_url(
        approval_info=FinalReviewApprovalInfo(
            url_id=url_mapping.url_id,
            record_type=RecordType.ARREST_RECORDS,
            relevant=True,
        ),
        user_id=1
    )

    # Confirm same agency id is listed as confirmed
    urls: list[URL] = await adb_client.get_all(URL)
    assert len(urls) == 1
    url = urls[0]
    assert url.id == url_mapping.url_id
    assert url.record_type == RecordType.ARREST_RECORDS.value
    assert url.outcome == URLStatus.VALIDATED.value
    assert url.name == "Test Name"
    assert url.description == "Test Description"

    confirmed_agency: list[ConfirmedURLAgency] = await adb_client.get_all(ConfirmedURLAgency)
    assert len(confirmed_agency) == 1
    assert confirmed_agency[0].url_id == url_mapping.url_id
    assert confirmed_agency[0].agency_id == agency_id

    approving_user_urls: list[ReviewingUserURL] = await adb_client.get_all(ReviewingUserURL)
    assert len(approving_user_urls) == 1
    assert approving_user_urls[0].user_id == 1
    assert approving_user_urls[0].url_id == url_mapping.url_id

    optional_metadata: list[URLOptionalDataSourceMetadata] = await adb_client.get_all(URLOptionalDataSourceMetadata)
    assert len(optional_metadata) == 1
    assert optional_metadata[0].url_id == url_mapping.url_id
    assert optional_metadata[0].record_formats == ["Test Record Format", "Test Record Format 2"]
    assert optional_metadata[0].data_portal_type == "Test Data Portal Type"
    assert optional_metadata[0].supplying_entity == "Test Supplying Entity"

@pytest.mark.asyncio
async def test_approval_url_error(db_data_creator: DBDataCreator):
    setup_info = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True,
        include_miscellaneous_metadata=False
    )
    url_mapping = setup_info.url_mapping

    # Set all required descriptors to none and receive an error
    adb_client = db_data_creator.adb_client
    with pytest.raises(HTTPException) as e:
        await adb_client.approve_url(
            approval_info=FinalReviewApprovalInfo(
                url_id=url_mapping.url_id,
            ),
            user_id=1
        )
        assert e.value.status_code == 422

    # Create kwarg dictionary with all required approval info fields
    kwarg_dict = {
        "record_type": RecordType.ARREST_RECORDS,
        "agency_ids": [await db_data_creator.agency()],
        "name": "Test Name",
        "description": "Test Description",
    }
    # For each keyword, create a copy of the kwargs and set that one to none
    # Confirm it produces the correct error
    for kwarg in kwarg_dict:
        kwarg_copy = kwarg_dict.copy()
        kwarg_copy[kwarg] = None
        with pytest.raises(HTTPException) as e:
            await adb_client.approve_url(
                approval_info=FinalReviewApprovalInfo(
                    url_id=url_mapping.url_id,
                    relevant=True,
                    **kwarg_copy
                ),
                user_id=1
            )
            pytest.fail(f"Expected error for kwarg {kwarg}")

    # Test that if all kwargs are set, no error is raised
    await adb_client.approve_url(
        approval_info=FinalReviewApprovalInfo(
            url_id=url_mapping.url_id,
            relevant=True,
            **kwarg_dict
        ),
        user_id=1
    )

@pytest.mark.asyncio
async def test_get_next_url_for_user_relevance_annotation_pending(
        db_data_creator: DBDataCreator
):
    setup_info = await setup_for_get_next_url_for_annotation(
        db_data_creator=db_data_creator,
        url_count=2
    )

    url_1 = setup_info.insert_urls_info.url_mappings[0]

    # Add `Relevancy` attribute with value `True`
    await db_data_creator.auto_relevant_suggestions(
        url_id=url_1.url_id,
        relevant=True
    )

    adb_client = db_data_creator.adb_client
    url = await adb_client.get_next_url_for_relevance_annotation(
        user_id=1,
        batch_id=None
    )
    assert url is not None

@pytest.mark.asyncio
async def test_get_next_url_for_annotation_batch_filtering(
        db_data_creator: DBDataCreator
):
    """
    Test that for all annotation retrievals, batch filtering works as expected
    """
    setup_info_1 = await setup_for_get_next_url_for_annotation(
        db_data_creator=db_data_creator,
        url_count=1
    )
    setup_info_2 = await setup_for_get_next_url_for_annotation(
        db_data_creator=db_data_creator,
        url_count=1
    )

    url_1 = setup_info_1.insert_urls_info.url_mappings[0]
    url_2 = setup_info_2.insert_urls_info.url_mappings[0]

    # Test for relevance
    # If a batch id is provided, return first valid URL with that batch id
    result_with_batch_id = await db_data_creator.adb_client.get_next_url_for_relevance_annotation(
        user_id=1,
        batch_id=setup_info_2.batch_id
    )

    assert result_with_batch_id.url_info.url == url_2.url

    # If no batch id is provided, return first valid URL
    result_no_batch_id = await db_data_creator.adb_client.get_next_url_for_relevance_annotation(
        user_id=1,
        batch_id=None
    )

    assert result_no_batch_id.url_info.url == url_1.url

    # Test for record type
    # If a batch id is provided, return first valid URL with that batch id
    result_with_batch_id = await db_data_creator.adb_client.get_next_url_for_record_type_annotation(
        user_id=1,
        batch_id=setup_info_2.batch_id
    )

    assert result_with_batch_id.url_info.url == url_2.url

    # If no batch id is provided, return first valid URL
    result_no_batch_id = await db_data_creator.adb_client.get_next_url_for_record_type_annotation(
        user_id=1,
        batch_id=None
    )

    assert result_no_batch_id.url_info.url == url_1.url

    # Test for agency
    for url in [url_1, url_2]:
        await db_data_creator.auto_suggestions(
            url_ids=[url.url_id],
            num_suggestions=2,
            suggestion_type=SuggestionType.AUTO_SUGGESTION
        )

    # If a batch id is provided, return first valid URL with that batch id
    result_with_batch_id = await db_data_creator.adb_client.get_next_url_agency_for_annotation(
        user_id=1,
        batch_id=setup_info_2.batch_id
    )

    assert result_with_batch_id.next_annotation.url == url_2.url

    # If no batch id is provided, return first valid URL
    result_no_batch_id = await db_data_creator.adb_client.get_next_url_agency_for_annotation(
        user_id=1,
        batch_id=None
    )

    assert result_no_batch_id.next_annotation.url == url_1.url


@pytest.mark.asyncio
async def test_get_next_url_for_user_relevance_annotation_validated(
        db_data_creator: DBDataCreator
):
    """
    A validated URL should not turn up in get_next_url_for_user_annotation
    """

    setup_info = await setup_for_get_next_url_for_annotation(
        db_data_creator=db_data_creator,
        url_count=1,
        outcome=URLStatus.VALIDATED
    )


    url_1 = setup_info.insert_urls_info.url_mappings[0]

    # Add `Relevancy` attribute with value `True`
    await db_data_creator.auto_relevant_suggestions(
        url_id=url_1.url_id,
        relevant=True
    )

    adb_client = db_data_creator.adb_client
    url = await adb_client.get_next_url_for_relevance_annotation(
        user_id=1,
        batch_id=None
    )
    assert url is None

@pytest.mark.asyncio
async def test_annotate_url_marked_not_relevant(db_data_creator: DBDataCreator):
    """
    If a URL is marked not relevant by the user, they should not receive that URL
    in calls to get an annotation for record type or agency
    Other users should still receive the URL
    """
    setup_info = await setup_for_get_next_url_for_annotation(
        db_data_creator=db_data_creator,
        url_count=2
    )
    adb_client = db_data_creator.adb_client
    url_to_mark_not_relevant: URLMapping = setup_info.insert_urls_info.url_mappings[0]
    url_to_mark_relevant: URLMapping = setup_info.insert_urls_info.url_mappings[1]
    for url_mapping in setup_info.insert_urls_info.url_mappings:
        await db_data_creator.agency_auto_suggestions(
            url_id=url_mapping.url_id,
            count=3
        )
    await adb_client.add_user_relevant_suggestion(
        user_id=1,
        url_id=url_to_mark_not_relevant.url_id,
        relevant=False
    )
    await adb_client.add_user_relevant_suggestion(
        user_id=1,
        url_id=url_to_mark_relevant.url_id,
        relevant=True
    )

    # User should not receive the URL for record type annotation
    record_type_annotation_info = await adb_client.get_next_url_for_record_type_annotation(
        user_id=1,
        batch_id=None
    )
    assert record_type_annotation_info.url_info.url_id != url_to_mark_not_relevant.url_id

    # Other users should still receive the URL for record type annotation
    record_type_annotation_info = await adb_client.get_next_url_for_record_type_annotation(
        user_id=2,
        batch_id=None
    )
    assert record_type_annotation_info.url_info.url_id == url_to_mark_not_relevant.url_id

    # User should not receive the URL for agency annotation
    agency_annotation_info = await adb_client.get_next_url_agency_for_annotation(
        user_id=1,
        batch_id=None
    )
    assert agency_annotation_info.next_annotation.url_id != url_to_mark_not_relevant.url_id

    # Other users should still receive the URL for agency annotation
    agency_annotation_info = await adb_client.get_next_url_agency_for_annotation(
        user_id=2,
        batch_id=None
    )
    assert agency_annotation_info.next_annotation.url_id == url_to_mark_not_relevant.url_id

@pytest.mark.asyncio
async def test_annotate_url_agency_agency_not_in_db(db_data_creator: DBDataCreator):
    setup_info = await setup_for_annotate_agency(
        db_data_creator,
        url_count=1
    )

    url_id = setup_info.url_ids[0]
    await db_data_creator.adb_client.add_agency_manual_suggestion(
        agency_id=1,
        url_id=url_id,
        user_id=1,
        is_new=False
    )

    agencies = await db_data_creator.adb_client.get_all(Agency)
    assert len(agencies)
    assert agencies[0].name == PLACEHOLDER_AGENCY_NAME