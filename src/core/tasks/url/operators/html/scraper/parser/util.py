from urllib.parse import urlparse

from src.db.dtos.url.html_content import URLHTMLContentInfo
from src.core.tasks.url.operators.html.scraper.parser.mapping import ENUM_TO_ATTRIBUTE_MAPPING
from src.core.tasks.url.operators.html.scraper.parser.dtos.response_html import ResponseHTMLInfo


def convert_to_response_html_info(
    html_content_infos: list[URLHTMLContentInfo]
) -> ResponseHTMLInfo:
    response_html_info = ResponseHTMLInfo()

    for html_content_info in html_content_infos:
        setattr(response_html_info, ENUM_TO_ATTRIBUTE_MAPPING[html_content_info.content_type], html_content_info.content)

    return response_html_info


def remove_excess_whitespace(s: str) -> str:
    """Removes leading, trailing, and excess adjacent whitespace.

    Args:
        s (str): String to remove whitespace from.

    Returns:
        str: Clean string with excess whitespace stripped.
    """
    return " ".join(s.split()).strip()


def add_https(url: str) -> str:
    if not url.startswith("http"):
        url = "https://" + url
    return url


def remove_trailing_backslash(url_path: str) -> str:
    if url_path and url_path[-1] == "/":
        url_path = url_path[:-1]
    return url_path


def drop_hostname(new_url: str) -> str:
    url_path = urlparse(new_url).path[1:]
    return url_path
