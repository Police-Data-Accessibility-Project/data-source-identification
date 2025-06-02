from pydantic import BaseModel

from src.db.dtos.url_html_content_info import URLHTMLContentInfo


class URLWithHTML(BaseModel):
    url_id: int
    url: str
    html_infos: list[URLHTMLContentInfo]