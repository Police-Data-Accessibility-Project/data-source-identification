from dataclasses import dataclass

from src.db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo, HTMLContentType


@dataclass
class ResponseHTMLInfo:
    index: int = -1
    url: str = ""
    url_path: str = ""
    title: str = ""
    description: str = ""
    root_page_title: str = ""
    http_response: int = -1
    h1: str = ""
    h2: str = ""
    h3: str = ""
    h4: str = ""
    h5: str = ""
    h6: str = ""
    div: str = ""

ENUM_TO_ATTRIBUTE_MAPPING = {
    HTMLContentType.TITLE: "title",
    HTMLContentType.DESCRIPTION: "description",
    HTMLContentType.H1: "h1",
    HTMLContentType.H2: "h2",
    HTMLContentType.H3: "h3",
    HTMLContentType.H4: "h4",
    HTMLContentType.H5: "h5",
    HTMLContentType.H6: "h6",
    HTMLContentType.DIV: "div"
}

def convert_to_response_html_info(html_content_infos: list[URLHTMLContentInfo]):
    response_html_info = ResponseHTMLInfo()

    for html_content_info in html_content_infos:
        setattr(response_html_info, ENUM_TO_ATTRIBUTE_MAPPING[html_content_info.content_type], html_content_info.content)

    return response_html_info