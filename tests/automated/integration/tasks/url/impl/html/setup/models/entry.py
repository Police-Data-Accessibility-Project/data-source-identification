from enum import Enum
from http import HTTPStatus

from pydantic import BaseModel

from src.collectors.enums import URLStatus
from src.db.models.impl.url.scrape_info.enums import ScrapeStatus


class TestErrorType(Enum):
    SCRAPER = "scraper"
    HTTP_404 = "http-404"


class TestWebMetadataInfo(BaseModel):
    accessed: bool
    content_type: str | None
    response_code: HTTPStatus
    error_message: str | None

class TestURLInfo(BaseModel):
    url: str
    status: URLStatus

class ExpectedResult(BaseModel):
    has_html: bool
    scrape_status: ScrapeStatus | None  # Does not have scrape info if none
    web_metadata_status_marked_404: bool = False

class TestURLHTMLTaskSetupEntry(BaseModel):
    url_info: TestURLInfo
    web_metadata_info: TestWebMetadataInfo | None
    give_error: TestErrorType | None = None
    expected_result: ExpectedResult