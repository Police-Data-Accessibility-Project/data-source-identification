from src.db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo


def dictify_html_info(html_infos: list[URLHTMLContentInfo]) -> dict[str, str]:
    d = {}
    for html_info in html_infos:
        d[html_info.content_type.value] = html_info.content
    return d
