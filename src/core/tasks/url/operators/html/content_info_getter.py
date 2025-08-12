from src.core.tasks.url.operators.html.scraper.parser.dtos.response_html import ResponseHTMLInfo
from src.db.dtos.url.html_content import URLHTMLContentInfo
from src.db.models.impl.url.html.content.enums import HTMLContentType


class HTMLContentInfoGetter:

    def __init__(self, response_html_info: ResponseHTMLInfo, url_id: int):
        self.response_html_info = response_html_info
        self.url_id = url_id
        self.html_content_infos = []

    def get_all_html_content(self) -> list[URLHTMLContentInfo]:
        for content_type in HTMLContentType:
            self.add_html_content(content_type)
        return self.html_content_infos

    def add_html_content(self, content_type: HTMLContentType):
        lower_str = content_type.value.lower()
        val = getattr(self.response_html_info, lower_str)
        if val is None or val.strip() == "":
            return
        uhci = URLHTMLContentInfo(
            url_id=self.url_id,
            content_type=content_type,
            content=val
        )
        self.html_content_infos.append(uhci)
