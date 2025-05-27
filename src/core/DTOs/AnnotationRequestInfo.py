from pydantic import BaseModel

from src.html_tag_collector import ResponseHTMLInfo


class AnnotationRequestInfo(BaseModel):
    url: str
    metadata_id: int
    html_info: ResponseHTMLInfo
    suggested_value: str