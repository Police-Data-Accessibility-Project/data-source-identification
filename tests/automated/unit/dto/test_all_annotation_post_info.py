import pytest

from src.core.DTOs.AllAnnotationPostInfo import AllAnnotationPostInfo
from src.core.enums import RecordType, SuggestedStatus
from src.core.exceptions import FailedValidationException

# Mock values to pass
mock_record_type = RecordType.ARREST_RECORDS.value  # replace with valid RecordType if Enum
mock_agency = {"is_new": False, "suggested_agency": 1}  # replace with a valid dict for the URLAgencyAnnotationPostInfo model

@pytest.mark.parametrize(
    "suggested_status, record_type, agency, should_raise",
    [
        (SuggestedStatus.RELEVANT,  mock_record_type, mock_agency, False),  # valid
        (SuggestedStatus.RELEVANT,  None,            mock_agency, True),   # missing record_type
        (SuggestedStatus.RELEVANT,  mock_record_type, None,       True),   # missing agency
        (SuggestedStatus.RELEVANT,  None,            None,        True),   # missing both
        (SuggestedStatus.NOT_RELEVANT, None,            None,        False),  # valid
        (SuggestedStatus.NOT_RELEVANT, mock_record_type, None,       True),   # record_type present
        (SuggestedStatus.NOT_RELEVANT, None,            mock_agency, True),   # agency present
        (SuggestedStatus.NOT_RELEVANT, mock_record_type, mock_agency, True),  # both present
    ]
)
def test_all_annotation_post_info_validation(suggested_status, record_type, agency, should_raise):
    data = {
        "suggested_status": suggested_status.value,
        "record_type": record_type,
        "agency": agency
    }

    if should_raise:
        with pytest.raises(FailedValidationException):
            AllAnnotationPostInfo(**data)
    else:
        model = AllAnnotationPostInfo(**data)
        assert model.suggested_status == suggested_status
