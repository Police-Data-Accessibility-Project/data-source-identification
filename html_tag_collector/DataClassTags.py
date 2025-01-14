from dataclasses import dataclass


@dataclass
class ResponseHTMLInfo:
    index: int = None
    url: str = ""
    url_path: str = ""
    html_title: str = ""
    meta_description: str = ""
    root_page_title: str = ""
    http_response: int = -1
    h1: str = ""
    h2: str = ""
    h3: str = ""
    h4: str = ""
    h5: str = ""
    h6: str = ""
    div_text: str = ""
