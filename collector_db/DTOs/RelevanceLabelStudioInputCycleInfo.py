from pydantic import BaseModel

from collector_db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo


class RelevanceLabelStudioInputCycleInfo(BaseModel):
    url: str
    metadata_id: int
    html_content_info: list[URLHTMLContentInfo]