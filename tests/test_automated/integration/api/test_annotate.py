from typing import Any

import pytest

from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from collector_db.DTOs.URLMapping import URLMapping
from collector_db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource
from collector_db.models import UserUrlAgencySuggestion, UserRelevantSuggestion, UserRecordTypeSuggestion
from core.DTOs.GetNextRecordTypeAnnotationResponseInfo import GetNextRecordTypeAnnotationResponseOuterInfo
from core.DTOs.GetNextRelevanceAnnotationResponseInfo import GetNextRelevanceAnnotationResponseOuterInfo
from core.DTOs.GetNextURLForAgencyAnnotationResponse import URLAgencyAnnotationPostInfo
from core.DTOs.GetNextURLForAnnotationResponse import GetNextURLForAnnotationResponse
from core.DTOs.RecordTypeAnnotationPostInfo import RecordTypeAnnotationPostInfo
from core.DTOs.RelevanceAnnotationPostInfo import RelevanceAnnotationPostInfo
from core.enums import RecordType, SuggestionType
from tests.helpers.complex_test_data_functions import AnnotateAgencySetupInfo, setup_for_annotate_agency
from html_tag_collector.DataClassTags import ResponseHTMLInfo
from tests.helpers.DBDataCreator import BatchURLCreationInfo
from tests.test_automated.integration.api.conftest import MOCK_USER_ID

def check_url_mappings_match(
    map_1: URLMapping,
    map_2: URLMapping
):
    assert map_1.url_id == map_2.url_id
    assert map_2.url == map_2.url

def check_html_info_not_empty(
    html_info: ResponseHTMLInfo
):
    assert html_info.description != ""
    assert html_info.title != ""

@pytest.mark.asyncio
async def test_annotate_relevancy(api_test_helper):
    ath = api_test_helper

    batch_id = ath.db_data_creator.batch()

    # Create 2 URLs with outcome `pending`
    iui: InsertURLsInfo = ath.db_data_creator.urls(batch_id=batch_id, url_count=2)

    url_1 = iui.url_mappings[0]
    url_2 = iui.url_mappings[1]

    # Add `Relevancy` attribute with value `True` to 1st URL
    await ath.db_data_creator.auto_relevant_suggestions(
        url_id=url_1.url_id,
        relevant=True
    )

    # Add 'Relevancy' attribute with value `False` to 2nd URL
    await ath.db_data_creator.auto_relevant_suggestions(
        url_id=url_2.url_id,
        relevant=False
    )

    # Add HTML data to both
    await ath.db_data_creator.html_data([url_1.url_id, url_2.url_id])
    # Call `GET` `/annotate/relevance` and receive next URL
    request_info_1: GetNextRelevanceAnnotationResponseOuterInfo = api_test_helper.request_validator.get_next_relevance_annotation()
    inner_info_1 = request_info_1.next_annotation

    check_url_mappings_match(inner_info_1.url_info, url_1)
    check_html_info_not_empty(inner_info_1.html_info)

    # Validate that the correct relevant value is returned
    assert inner_info_1.suggested_relevant is True

    #  Annotate with value 'False' and get next URL
    request_info_2: GetNextRelevanceAnnotationResponseOuterInfo = api_test_helper.request_validator.post_relevance_annotation_and_get_next(
        url_id=inner_info_1.url_info.url_id,
        relevance_annotation_post_info=RelevanceAnnotationPostInfo(
            is_relevant=False
        )
    )

    inner_info_2 = request_info_2.next_annotation

    check_url_mappings_match(
        inner_info_2.url_info,
        url_2
    )
    check_html_info_not_empty(inner_info_2.html_info)

    request_info_3: GetNextRelevanceAnnotationResponseOuterInfo = api_test_helper.request_validator.post_relevance_annotation_and_get_next(
        url_id=inner_info_2.url_info.url_id,
        relevance_annotation_post_info=RelevanceAnnotationPostInfo(
            is_relevant=True
        )
    )

    assert request_info_3.next_annotation is None

    # Get all URL annotations. Confirm they exist for user
    adb_client = ath.adb_client()
    results: list[UserRelevantSuggestion] = await adb_client.get_all(UserRelevantSuggestion)
    result_1 = results[0]
    result_2 = results[1]

    assert result_1.url_id == inner_info_1.url_info.url_id
    assert result_1.relevant is False

    assert result_2.url_id == inner_info_2.url_info.url_id
    assert result_2.relevant is True

    # If user submits annotation for same URL, the URL should be overwritten

    request_info_4: GetNextRelevanceAnnotationResponseOuterInfo = api_test_helper.request_validator.post_relevance_annotation_and_get_next(
        url_id=inner_info_1.url_info.url_id,
        relevance_annotation_post_info=RelevanceAnnotationPostInfo(
            is_relevant=True
        )
    )

    assert request_info_4.next_annotation is None

    results: list[UserRelevantSuggestion] = await adb_client.get_all(UserRelevantSuggestion)
    assert len(results) == 2

    for result in results:
        if result.url_id == inner_info_1.url_info.url_id:
            assert results[0].relevant is True



@pytest.mark.asyncio
async def test_annotate_record_type(api_test_helper):
    ath = api_test_helper

    batch_id = ath.db_data_creator.batch()

    # Create 2 URLs with outcome `pending`
    iui: InsertURLsInfo = ath.db_data_creator.urls(batch_id=batch_id, url_count=2)

    url_1 = iui.url_mappings[0]
    url_2 = iui.url_mappings[1]

    # Add record type attribute with value `Accident Reports` to 1st URL
    await ath.db_data_creator.auto_record_type_suggestions(
        url_id=url_1.url_id,
        record_type=RecordType.ACCIDENT_REPORTS
    )

    # Add 'Record Type' attribute with value `Dispatch Recordings` to 2nd URL
    await ath.db_data_creator.auto_record_type_suggestions(
        url_id=url_2.url_id,
        record_type=RecordType.DISPATCH_RECORDINGS
    )

    # Add HTML data to both
    await ath.db_data_creator.html_data([url_1.url_id, url_2.url_id])

    # Call `GET` `/annotate/record-type` and receive next URL
    request_info_1: GetNextRecordTypeAnnotationResponseOuterInfo = api_test_helper.request_validator.get_next_record_type_annotation()
    inner_info_1 = request_info_1.next_annotation

    check_url_mappings_match(inner_info_1.url_info, url_1)
    check_html_info_not_empty(inner_info_1.html_info)

    # Validate that the correct record type is returned
    assert inner_info_1.suggested_record_type == RecordType.ACCIDENT_REPORTS

    # Annotate with value 'Personnel Records' and get next URL
    request_info_2: GetNextRecordTypeAnnotationResponseOuterInfo = api_test_helper.request_validator.post_record_type_annotation_and_get_next(
        url_id=inner_info_1.url_info.url_id,
        record_type_annotation_post_info=RecordTypeAnnotationPostInfo(
            record_type=RecordType.PERSONNEL_RECORDS
        )
    )

    inner_info_2 = request_info_2.next_annotation

    check_url_mappings_match(inner_info_2.url_info, url_2)
    check_html_info_not_empty(inner_info_2.html_info)

    request_info_3: GetNextRecordTypeAnnotationResponseOuterInfo = api_test_helper.request_validator.post_record_type_annotation_and_get_next(
        url_id=inner_info_2.url_info.url_id,
        record_type_annotation_post_info=RecordTypeAnnotationPostInfo(
            record_type=RecordType.ANNUAL_AND_MONTHLY_REPORTS
        )
    )

    assert request_info_3.next_annotation is None

    # Get all URL annotations. Confirm they exist for user
    adb_client = ath.adb_client()
    results: list[UserRecordTypeSuggestion] = await adb_client.get_all(UserRecordTypeSuggestion)
    result_1 = results[0]
    result_2 = results[1]

    assert result_1.url_id == inner_info_1.url_info.url_id
    assert result_1.record_type == RecordType.PERSONNEL_RECORDS.value

    assert result_2.url_id == inner_info_2.url_info.url_id
    assert result_2.record_type == RecordType.ANNUAL_AND_MONTHLY_REPORTS.value

    # If user submits annotation for same URL, the URL should be overwritten

    request_info_4: GetNextRecordTypeAnnotationResponseOuterInfo = api_test_helper.request_validator.post_record_type_annotation_and_get_next(
        url_id=inner_info_1.url_info.url_id,
        record_type_annotation_post_info=RecordTypeAnnotationPostInfo(
            record_type=RecordType.BOOKING_REPORTS
        )
    )

    assert request_info_4.next_annotation is None

    results: list[UserRecordTypeSuggestion] = await adb_client.get_all(UserRecordTypeSuggestion)
    assert len(results) == 2

    for result in results:
        if result.url_id == inner_info_1.url_info.url_id:
            assert result.record_type == RecordType.BOOKING_REPORTS.value


@pytest.mark.asyncio
async def test_annotate_agency_multiple_auto_suggestions(api_test_helper):
    """
    Test Scenario: Multiple Auto Suggestions
    A URL has multiple Agency Auto Suggestion and has not been annotated by the User
    The user should receive all of the auto suggestions with full detail
    """
    ath = api_test_helper
    buci: BatchURLCreationInfo = await ath.db_data_creator.batch_and_urls(
        url_count=1,
        with_html_content=True
    )
    await ath.db_data_creator.auto_suggestions(
        url_ids=buci.url_ids,
        num_suggestions=2,
        suggestion_type=SuggestionType.AUTO_SUGGESTION
    )

    # User requests next annotation
    response = await ath.request_validator.get_next_agency_annotation()

    assert response.next_annotation
    next_annotation = response.next_annotation
    # Check that url_id matches the one we inserted
    assert next_annotation.url_id == buci.url_ids[0]

    # Check that html data is present
    assert next_annotation.html_info.description != ""
    assert next_annotation.html_info.title != ""

    # Check that two agency_suggestions exist
    assert len(next_annotation.agency_suggestions) == 2

    for agency_suggestion in next_annotation.agency_suggestions:
        assert agency_suggestion.suggestion_type == SuggestionType.AUTO_SUGGESTION
        assert agency_suggestion.pdap_agency_id is not None
        assert agency_suggestion.agency_name is not None
        assert agency_suggestion.state is not None
        assert agency_suggestion.county is not None
        assert agency_suggestion.locality is not None


@pytest.mark.asyncio
async def test_annotate_agency_single_unknown_auto_suggestion(api_test_helper):
    """
    Test Scenario: Single Unknown Auto Suggestion
    A URL has a single Unknown Agency Auto Suggestion and has not been annotated by the User
    The user should receive a single Unknown Auto Suggestion lacking other detail
    """
    ath = api_test_helper
    buci: BatchURLCreationInfo = await ath.db_data_creator.batch_and_urls(
        url_count=1,
        with_html_content=True
    )
    await ath.db_data_creator.auto_suggestions(
        url_ids=buci.url_ids,
        num_suggestions=1,
        suggestion_type=SuggestionType.UNKNOWN
    )
    response = await ath.request_validator.get_next_agency_annotation()

    assert response.next_annotation
    next_annotation = response.next_annotation
    # Check that url_id matches the one we inserted
    assert next_annotation.url_id == buci.url_ids[0]

    # Check that html data is present
    assert next_annotation.html_info.description != ""
    assert next_annotation.html_info.title != ""

    # Check that one agency_suggestion exists
    assert len(next_annotation.agency_suggestions) == 1

    agency_suggestion = next_annotation.agency_suggestions[0]

    assert agency_suggestion.suggestion_type == SuggestionType.UNKNOWN
    assert agency_suggestion.pdap_agency_id is None
    assert agency_suggestion.agency_name is None
    assert agency_suggestion.state is None
    assert agency_suggestion.county is None
    assert agency_suggestion.locality is None


@pytest.mark.asyncio
async def test_annotate_agency_single_confirmed_agency(api_test_helper):
    """
    Test Scenario: Single Confirmed Agency
    A URL has a single Confirmed Agency and has not been annotated by the User
    The user should not receive this URL to annotate
    """
    ath = api_test_helper
    buci: BatchURLCreationInfo = await ath.db_data_creator.batch_and_urls(
        url_count=1,
        with_html_content=True
    )
    await ath.db_data_creator.confirmed_suggestions(
        url_ids=buci.url_ids,
    )
    response = await ath.request_validator.get_next_agency_annotation()
    assert response.next_annotation is None

@pytest.mark.asyncio
async def test_annotate_agency_other_user_annotation(api_test_helper):
    """
    Test Scenario: Other User Annotation
    A URL has been annotated by another User
    Our user should still receive this URL to annotate
    """
    ath = api_test_helper
    setup_info: AnnotateAgencySetupInfo = await setup_for_annotate_agency(
        db_data_creator=ath.db_data_creator,
        url_count=1
    )
    url_ids = setup_info.url_ids


    await ath.db_data_creator.manual_suggestion(
        user_id=MOCK_USER_ID + 1,
        url_id=url_ids[0],
    )

    response = await ath.request_validator.get_next_agency_annotation()

    assert response.next_annotation
    next_annotation = response.next_annotation
    # Check that url_id matches the one we inserted
    assert next_annotation.url_id == url_ids[0]

    # Check that html data is present
    assert next_annotation.html_info.description != ""
    assert next_annotation.html_info.title != ""

    # Check that one agency_suggestion exists
    assert len(next_annotation.agency_suggestions) == 1

@pytest.mark.asyncio
async def test_annotate_agency_submit_and_get_next(api_test_helper):
    """
    Test Scenario: Submit and Get Next (no other URL available)
    A URL has been annotated by our User, and no other valid URLs have not been annotated
    Our user should not receive another URL to annotate
    Until another relevant URL is added
    """
    ath = api_test_helper
    setup_info: AnnotateAgencySetupInfo = await setup_for_annotate_agency(
        db_data_creator=ath.db_data_creator,
        url_count=2
    )
    url_ids = setup_info.url_ids

    # User should submit an annotation and receive the next
    response = await ath.request_validator.post_agency_annotation_and_get_next(
        url_id=url_ids[0],
        agency_annotation_post_info=URLAgencyAnnotationPostInfo(
            suggested_agency=await ath.db_data_creator.agency(),
            is_new=False
        )

    )
    assert response.next_annotation is not None

    # User should submit this annotation and receive none for the next
    response = await ath.request_validator.post_agency_annotation_and_get_next(
        url_id=url_ids[1],
        agency_annotation_post_info=URLAgencyAnnotationPostInfo(
            suggested_agency=await ath.db_data_creator.agency(),
            is_new=False
        )
    )
    assert response.next_annotation is None


@pytest.mark.asyncio
async def test_annotate_agency_submit_new(api_test_helper):
    """
    Test Scenario: Submit New
    Our user receives an annotation and marks it as `NEW`
    This should complete successfully
    And within the database the annotation should be marked as `NEW`
    """
    ath = api_test_helper
    adb_client = ath.adb_client()
    setup_info: AnnotateAgencySetupInfo = await setup_for_annotate_agency(
        db_data_creator=ath.db_data_creator,
        url_count=1
    )
    url_ids = setup_info.url_ids

    # User should submit an annotation and mark it as New
    response = await ath.request_validator.post_agency_annotation_and_get_next(
        url_id=url_ids[0],
        agency_annotation_post_info=URLAgencyAnnotationPostInfo(
            suggested_agency=await ath.db_data_creator.agency(),
            is_new=True
        )
    )
    assert response.next_annotation is None

    # Within database, the annotation should be marked as `NEW`
    all_manual_suggestions = await adb_client.get_all(UserUrlAgencySuggestion)
    assert len(all_manual_suggestions) == 1
    assert all_manual_suggestions[0].is_new

