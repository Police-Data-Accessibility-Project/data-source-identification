from pydantic import BaseModel

from src.db.dtos.url.html_content import URLHTMLContentInfo


class URLAnnotationInfo(BaseModel):
    metadata_id: int
    url: str
    html_infos: list[URLHTMLContentInfo]
    suggested_value: str