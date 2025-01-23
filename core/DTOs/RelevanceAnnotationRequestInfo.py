from pydantic import BaseModel

from html_tag_collector.DataClassTags import ResponseHTMLInfo


class RelevanceAnnotationRequestInfo(BaseModel):
    url: str
    metadata_id: int
    html_info: ResponseHTMLInfo