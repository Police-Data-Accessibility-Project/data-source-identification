from pydantic import BaseModel

from html_tag_collector.DataClassTags import ResponseHTMLInfo


class AnnotationRequestInfo(BaseModel):
    url: str
    metadata_id: int
    html_info: ResponseHTMLInfo
    suggested_value: str