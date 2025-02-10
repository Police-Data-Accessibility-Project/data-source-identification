from typing import Any

import pytest

from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from collector_db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource
from collector_db.models import UserUrlAgencySuggestion
from core.DTOs.GetNextURLForAgencyAnnotationResponse import URLAgencyAnnotationPostInfo
from core.DTOs.GetNextURLForAnnotationResponse import GetNextURLForAnnotationResponse
from core.DTOs.RecordTypeAnnotationPostInfo import RecordTypeAnnotationPostInfo
from core.DTOs.RelevanceAnnotationPostInfo import RelevanceAnnotationPostInfo
from core.enums import RecordType, SuggestionType
from tests.helpers.DBDataCreator import BatchURLCreationInfo
from tests.test_automated.integration.api.conftest import MOCK_USER_ID

async def run_annotation_test(
    api_test_helper,
    submit_and_get_next_function: callable,
    get_next_function: callable,
    post_info: Any,
    metadata_attribute: URLMetadataAttributeType,
    expected_metadata_value: str
):
    ath = api_test_helper

    # Create batch with status `in-process` and strategy `example`
    batch_id = ath.db_data_creator.batch()
    # Create 2 URLs with outcome `pending`
    iui: InsertURLsInfo = ath.db_data_creator.urls(batch_id=batch_id, url_count=2)

    url_1 = iui.url_mappings[0]
    url_2 = iui.url_mappings[1]

    kwargs = {
        "attribute": metadata_attribute,
        "validation_status": ValidationStatus.PENDING_VALIDATION,
        "validation_source": ValidationSource.MACHINE_LEARNING
    }

    # Add `Relevancy` attribute with value `True` to 1st URL
    await ath.db_data_creator.metadata(
        url_ids=[url_1.url_id],
        **kwargs
    )
    # and `Relevancy` attribute with value `False` to 2nd other URL
    await ath.db_data_creator.metadata(
        url_ids=[url_2.url_id],
        **kwargs
    )

    # Add HTML data to both
    await ath.db_data_creator.html_data([url_1.url_id, url_2.url_id])
    # Call `GET` `/annotate/url` and receive next URL
    request_info_1: GetNextURLForAnnotationResponse = get_next_function()
    inner_info_1 = request_info_1.next_annotation

    # Validate presence of HTML data in `html` field
    assert inner_info_1.html_info.description != ""
    assert inner_info_1.html_info.title != ""
    assert inner_info_1.suggested_value == "False"

    # Call `POST` `/annotate/url` with finished annotation, and receive next URL
    request_info_2 = submit_and_get_next_function(
        inner_info_1.metadata_id,
        post_info
    )
    inner_info_2 = request_info_2.next_annotation
    # Confirm 2nd URL is distinct from 1st
    assert inner_info_1.url != inner_info_2.url

    # Validate presence of appropriate HTML data in `html` field
    assert inner_info_2.html_info.description != ""
    assert inner_info_2.html_info.title != ""

    # Validation annotation is present in database
    results = await api_test_helper.db_data_creator.adb_client.get_annotations_for_metadata_id(
        metadata_id=inner_info_1.metadata_id
    )
    assert len(results) == 1
    assert results[0].user_id == MOCK_USER_ID
    assert results[0].value == expected_metadata_value

    # Submit this one in turn, and no subsequent annotation info should be returned
    request_info_3 = submit_and_get_next_function(
        inner_info_2.metadata_id,
        post_info
    )

    assert request_info_3.next_annotation is None

@pytest.mark.asyncio
async def test_annotate_relevancy(api_test_helper):
    await run_annotation_test(
        api_test_helper=api_test_helper,
        submit_and_get_next_function=api_test_helper.request_validator.post_relevance_annotation_and_get_next,
        get_next_function=api_test_helper.request_validator.get_next_relevance_annotation,
        post_info=RelevanceAnnotationPostInfo(
            is_relevant=True
        ),
        metadata_attribute=URLMetadataAttributeType.RELEVANT,
        expected_metadata_value="True"
    )

@pytest.mark.asyncio
async def test_annotate_record_type(api_test_helper):
    await run_annotation_test(
        api_test_helper=api_test_helper,
        submit_and_get_next_function=api_test_helper.request_validator.post_record_type_annotation_and_get_next,
        get_next_function=api_test_helper.request_validator.get_next_record_type_annotation,
        post_info=RecordTypeAnnotationPostInfo(
            record_type=RecordType.ACCIDENT_REPORTS
        ),
        metadata_attribute=URLMetadataAttributeType.RECORD_TYPE,
        expected_metadata_value=RecordType.ACCIDENT_REPORTS.value
    )

@pytest.mark.asyncio
async def test_annotate_agency_multiple_auto_suggestions(api_test_helper):
    """
    Test Scenario: Multiple Auto Suggestions
    A URL has multiple Agency Auto Suggestion and has not been annotated by the User
    The user should receive all of the auto suggestions with full detail
    """
    ath = api_test_helper
    adb_client = ath.adb_client()
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
    adb_client = ath.adb_client()
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
    adb_client = ath.adb_client()
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
    adb_client = ath.adb_client()
    buci: BatchURLCreationInfo = await ath.db_data_creator.batch_and_urls(
        url_count=1,
        with_html_content=True
    )
    await ath.db_data_creator.auto_suggestions(
        url_ids=buci.url_ids,
        num_suggestions=1,
        suggestion_type=SuggestionType.UNKNOWN
    )

    await ath.db_data_creator.manual_suggestion(
        user_id=MOCK_USER_ID + 1,
        url_id=buci.url_ids[0],
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

@pytest.mark.asyncio
async def test_annotate_agency_submit_and_get_next(api_test_helper):
    """
    Test Scenario: Submit and Get Next (no other URL available)
    A URL has been annotated by our User, and no other valid URLs have not been annotated
    Our user should not receive another URL to annotate
    Until another relevant URL is added
    """
    ath = api_test_helper
    adb_client = ath.adb_client()
    buci: BatchURLCreationInfo = await ath.db_data_creator.batch_and_urls(
        url_count=2,
        with_html_content=True
    )
    await ath.db_data_creator.auto_suggestions(
        url_ids=buci.url_ids,
        num_suggestions=1,
        suggestion_type=SuggestionType.UNKNOWN
    )

    # User should submit an annotation and receive the next
    response = await ath.request_validator.post_agency_annotation_and_get_next(
        url_id=buci.url_ids[0],
        agency_annotation_post_info=URLAgencyAnnotationPostInfo(
            suggested_agency=await ath.db_data_creator.agency(),
            is_new=False
        )

    )
    assert response.next_annotation is not None

    # User should submit this annotation and receive none for the next
    response = await ath.request_validator.post_agency_annotation_and_get_next(
        url_id=buci.url_ids[1],
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
    buci: BatchURLCreationInfo = await ath.db_data_creator.batch_and_urls(
        url_count=1,
        with_html_content=True
    )
    await ath.db_data_creator.auto_suggestions(
        url_ids=buci.url_ids,
        num_suggestions=1,
        suggestion_type=SuggestionType.UNKNOWN
    )

    # User should submit an annotation and mark it as New
    response = await ath.request_validator.post_agency_annotation_and_get_next(
        url_id=buci.url_ids[0],
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

