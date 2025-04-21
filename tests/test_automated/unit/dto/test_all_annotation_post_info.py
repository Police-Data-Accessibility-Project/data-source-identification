import pytest
from pydantic import ValidationError

from core.DTOs.AllAnnotationPostInfo import AllAnnotationPostInfo
from core.enums import RecordType
from core.exceptions import FailedValidationException

# Mock values to pass
mock_record_type = RecordType.ARREST_RECORDS.value  # replace with valid RecordType if Enum
mock_agency = {"is_new": False, "suggested_agency": 1}  # replace with a valid dict for the URLAgencyAnnotationPostInfo model

@pytest.mark.parametrize(
    "is_relevant, record_type, agency, should_raise",
    [
        (True,  mock_record_type, mock_agency, False),  # valid
        (True,  None,            mock_agency, True),   # missing record_type
        (True,  mock_record_type, None,       True),   # missing agency
        (True,  None,            None,        True),   # missing both
        (False, None,            None,        False),  # valid
        (False, mock_record_type, None,       True),   # record_type present
        (False, None,            mock_agency, True),   # agency present
        (False, mock_record_type, mock_agency, True),  # both present
    ]
)
def test_all_annotation_post_info_validation(is_relevant, record_type, agency, should_raise):
    data = {
        "is_relevant": is_relevant,
        "record_type": record_type,
        "agency": agency
    }

    if should_raise:
        with pytest.raises(FailedValidationException):
            AllAnnotationPostInfo(**data)
    else:
        model = AllAnnotationPostInfo(**data)
        assert model.is_relevant == is_relevant
