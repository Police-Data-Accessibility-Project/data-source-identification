from typing import Optional

from src.core.tasks.url.operators.html.scraper.parser.dtos.response_html import ResponseHTMLInfo


async def mock_parse(self, url: str, html_content: str, content_type: str) -> ResponseHTMLInfo:
    return ResponseHTMLInfo(
        url=url,
        title="fake title",
        description="fake description",
    )


async def mock_get_from_cache(self, url: str) -> Optional[str]:
    return None
