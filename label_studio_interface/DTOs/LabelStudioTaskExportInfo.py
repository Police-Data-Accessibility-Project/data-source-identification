from pydantic import BaseModel, Field

from collector_db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo, HTMLContentType


class LabelStudioTaskExportInfo(BaseModel):
    url: str
    html_title: str = ""
    meta_description: str = ""
    h1: list[str] = []
    h2: list[str] = []
    h3: list[str] = []
    h4: list[str] = []
    h5: list[str] = []
    h6: list[str] = []
    div_text: str = ""
    url_path: str = ""
    http_response: int = -1
    url_source_info: str = ""

ENUM_TO_ATTRIBUTE_MAPPING = {
    HTMLContentType.TITLE: "html_title",
    HTMLContentType.DESCRIPTION: "meta_description",
    HTMLContentType.H1: "h1",
    HTMLContentType.H2: "h2",
    HTMLContentType.H3: "h3",
    HTMLContentType.H4: "h4",
    HTMLContentType.H5: "h5",
    HTMLContentType.H6: "h6",
    HTMLContentType.DIV: "div_text"
}

def add_html_info_to_export_info(
        export_info: LabelStudioTaskExportInfo,
        html_content_info: URLHTMLContentInfo
):
    attribute_name = ENUM_TO_ATTRIBUTE_MAPPING[html_content_info.content_type]
    setattr(export_info, attribute_name, html_content_info.content)

