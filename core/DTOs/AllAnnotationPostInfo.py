from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, model_validator

from core.DTOs.GetNextURLForAgencyAnnotationResponse import URLAgencyAnnotationPostInfo
from core.enums import RecordType
from core.exceptions import FailedValidationException


class AllAnnotationPostInfo(BaseModel):
    is_relevant: bool
    record_type: Optional[RecordType] = None
    agency: Optional[URLAgencyAnnotationPostInfo] = None

    @model_validator(mode="before")
    def allow_record_type_and_agency_only_if_relevant(cls, values):
        is_relevant = values.get("is_relevant")
        record_type = values.get("record_type")
        agency = values.get("agency")

        if not is_relevant:
            if record_type is not None:
                raise FailedValidationException("record_type must be None if is_relevant is False")

            if agency is not None:
                raise FailedValidationException("agency must be None if is_relevant is False")
            return values
        # Similarly, if relevant, record_type and agency must be provided
        if record_type is None:
            raise FailedValidationException("record_type must be provided if is_relevant is True")
        if agency is None:
            raise FailedValidationException("agency must be provided if is_relevant is True")
        return values