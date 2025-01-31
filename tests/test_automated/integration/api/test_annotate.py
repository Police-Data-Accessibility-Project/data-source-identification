from typing import Any

import pytest

from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from collector_db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource
from core.DTOs.GetNextURLForAnnotationResponse import GetNextURLForAnnotationResponse
from core.DTOs.RecordTypeAnnotationPostInfo import RecordTypeAnnotationPostInfo
from core.DTOs.RelevanceAnnotationPostInfo import RelevanceAnnotationPostInfo
from core.enums import RecordType
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
    request_info_3 = ath.request_validator.post_relevance_annotation_and_get_next(
        metadata_id=inner_info_2.metadata_id,
        relevance_annotation_post_info=post_info
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
