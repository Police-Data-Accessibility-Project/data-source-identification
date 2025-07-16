from typing import Optional

from pydantic import BaseModel, model_validator

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.core.enums import RecordType, SuggestedStatus
from src.core.exceptions import FailedValidationException


class AllAnnotationPostInfo(BaseModel):
    suggested_status: SuggestedStatus
    record_type: Optional[RecordType] = None
    agency: Optional[URLAgencyAnnotationPostInfo] = None

    @model_validator(mode="after")
    def allow_record_type_and_agency_only_if_relevant(self):
        suggested_status = self.suggested_status
        record_type = self.record_type
        agency = self.agency

        if suggested_status != SuggestedStatus.RELEVANT:
            if record_type is not None:
                raise FailedValidationException("record_type must be None if suggested_status is not relevant")

            if agency is not None:
                raise FailedValidationException("agency must be None if suggested_status is not relevant")
            return self
        # Similarly, if relevant, record_type and agency must be provided
        if record_type is None:
            raise FailedValidationException("record_type must be provided if suggested_status is relevant")
        if agency is None:
            raise FailedValidationException("agency must be provided if suggested_status is relevant")
        return self