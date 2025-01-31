from pydantic import BaseModel

from collector_db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo


class URLAnnotationInfo(BaseModel):
    metadata_id: int
    url: str
    html_infos: list[URLHTMLContentInfo]
    suggested_value: str