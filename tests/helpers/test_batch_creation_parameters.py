import datetime
from typing import Optional

from pydantic import BaseModel, model_validator

from src.collectors.enums import URLStatus, CollectorType
from src.core.enums import BatchStatus, RecordType, SuggestedStatus


class AnnotationInfo(BaseModel):
    user_relevant: Optional[SuggestedStatus] = None
    auto_relevant: Optional[bool] = None
    user_record_type: Optional[RecordType] = None
    auto_record_type: Optional[RecordType] = None
    user_agency: Optional[int] = None
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

class TestURLCreationParameters(BaseModel):
    count: int
    status: URLStatus = URLStatus.PENDING
    with_html_content: bool = False
    annotation_info: AnnotationInfo = AnnotationInfo()

    @model_validator(mode='after')
    def validate_annotation_info(self):
        if self.status == URLStatus.NOT_RELEVANT:
            self.annotation_info.final_review_approved = False
            return self
        if self.status != URLStatus.VALIDATED:
            return self

        # Assume is validated
        self.annotation_info.final_review_approved = True
        if self.annotation_info.user_record_type is None:
            self.annotation_info.user_record_type = RecordType.ARREST_RECORDS
        if self.annotation_info.user_agency is None:
            self.annotation_info.user_agency = 1


        return self

class TestBatchCreationParameters(BaseModel):
    created_at: Optional[datetime.datetime] = None
    outcome: BatchStatus = BatchStatus.READY_TO_LABEL
    strategy: CollectorType = CollectorType.EXAMPLE
    urls: Optional[list[TestURLCreationParameters]] = None

    @model_validator(mode='after')
    def validate_urls(self):
        if self.outcome != BatchStatus.READY_TO_LABEL:
            if self.urls is not None:
                raise ValueError('URLs cannot be provided if outcome is not READY_TO_LABEL')
            return self

        if self.urls is None:
            self.urls = [TestURLCreationParameters(count=1)]
        return self