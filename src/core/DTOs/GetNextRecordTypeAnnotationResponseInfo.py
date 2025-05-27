from typing import Optional

from pydantic import Field, BaseModel

from src.db.DTOs.URLMapping import URLMapping
from src.core.enums import RecordType
from src.html_tag_collector.DataClassTags import ResponseHTMLInfo


class GetNextRecordTypeAnnotationResponseInfo(BaseModel):
    url_info: URLMapping = Field(
        title="Information about the URL"
    )
    suggested_record_type: Optional[RecordType] = Field(
        title="What record type, if any, the auto-labeler identified the URL as"
    )
    html_info: ResponseHTMLInfo = Field(
        title="HTML information about the URL"
    )

class GetNextRecordTypeAnnotationResponseOuterInfo(BaseModel):
    next_annotation: Optional[GetNextRecordTypeAnnotationResponseInfo]
