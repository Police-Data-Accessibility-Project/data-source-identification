import pytest
from fastapi import HTTPException

from src.api.endpoints.review.dtos.approve import FinalReviewApprovalInfo
from src.core.enums import RecordType
from tests.helpers.complex_test_data_functions import setup_for_get_next_url_for_final_review
from tests.helpers.db_data_creator import DBDataCreator


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
