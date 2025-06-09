from pydantic import BaseModel, model_validator

from src.api.endpoints.annotate.dtos.agency.post import URLAgencyAnnotationPostInfo
from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from tests.helpers.batch_creation_parameters.annotation_info import AnnotationInfo


class TestURLCreationParameters(BaseModel):
    count: int = 1
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
            self.annotation_info.user_agency = URLAgencyAnnotationPostInfo(
                suggested_agency=1
            )


        return self
