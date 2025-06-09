from typing import Optional

from pydantic import BaseModel

from src.api.endpoints.annotate.dtos.agency.post import URLAgencyAnnotationPostInfo
from src.core.enums import SuggestedStatus, RecordType


class AnnotationInfo(BaseModel):
    user_relevant: Optional[SuggestedStatus] = None
    auto_relevant: Optional[bool] = None
    user_record_type: Optional[RecordType] = None
    auto_record_type: Optional[RecordType] = None
    user_agency: Optional[URLAgencyAnnotationPostInfo] = None
    auto_agency: Optional[int] = None
    confirmed_agency: Optional[int] = None
    final_review_approved: Optional[bool] = None

    def has_annotations(self):
        return any(value is not None for value in [
            self.user_relevant,
            self.auto_relevant,
            self.user_record_type,
            self.auto_record_type,
            self.user_agency,
            self.auto_agency,
            self.confirmed_agency,
            self.final_review_approved
        ])
