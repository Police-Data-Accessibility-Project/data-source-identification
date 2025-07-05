from pydantic import BaseModel

from src.db.dtos.url.html_content import URLHTMLContentInfo


class URLWithHTML(BaseModel):
    url_id: int
    url: str
    html_infos: list[URLHTMLContentInfo]