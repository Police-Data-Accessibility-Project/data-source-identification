from typing import Optional

from pydantic import Field, BaseModel

from src.api.endpoints.annotate.dtos.shared.base.response import AnnotationInnerResponseInfoBase
from src.core.enums import RecordType


class GetNextRecordTypeAnnotationResponseInfo(
    AnnotationInnerResponseInfoBase
):
    suggested_record_type: Optional[RecordType] = Field(
        title="What record type, if any, the auto-labeler identified the URL as"
    )

class GetNextRecordTypeAnnotationResponseOuterInfo(
    BaseModel
):
    next_annotation: Optional[GetNextRecordTypeAnnotationResponseInfo]
