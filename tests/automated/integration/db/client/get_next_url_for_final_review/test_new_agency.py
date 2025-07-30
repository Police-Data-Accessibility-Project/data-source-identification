import pytest

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.core.enums import SuggestedStatus, RecordType, SuggestionType
from tests.helpers.batch_creation_parameters.annotation_info import AnnotationInfo
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_get_next_url_for_final_review_new_agency(db_data_creator: DBDataCreator):
    """
    Test that a URL with a new agency is properly returned
    """

    # Apply batch v2
    parameters = TestBatchCreationParameters(
        urls=[
            TestURLCreationParameters(
                annotation_info=AnnotationInfo(
                    user_relevant=SuggestedStatus.RELEVANT,
                    user_agency=URLAgencyAnnotationPostInfo(
                        is_new=True
                    ),
                    user_record_type=RecordType.ARREST_RECORDS
                )
            )
        ]
    )
    creation_info = await db_data_creator.batch_v2(parameters)
    outer_result = await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=None
    )
    result = outer_result.next_source

    assert result is not None
    user_suggestion = result.annotations.agency.user
    assert user_suggestion.suggestion_type == SuggestionType.NEW_AGENCY
    assert user_suggestion.pdap_agency_id is None
    assert user_suggestion.agency_name is None
