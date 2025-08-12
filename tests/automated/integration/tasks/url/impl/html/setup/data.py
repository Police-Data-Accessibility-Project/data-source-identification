from http import HTTPStatus

from src.collectors.enums import URLStatus
from src.db.models.impl.url.scrape_info.enums import ScrapeStatus
from tests.automated.integration.tasks.url.impl.html.setup.models.entry import TestURLHTMLTaskSetupEntry, TestURLInfo, \
    TestWebMetadataInfo, ExpectedResult, TestErrorType

TEST_ENTRIES = [
    # URLs that give 200s should be updated with the appropriate scrape status
    #  and their html should be stored
    TestURLHTMLTaskSetupEntry(
        url_info=TestURLInfo(
            url="https://happy-path.com/pending",
            status=URLStatus.PENDING
        ),
        web_metadata_info=TestWebMetadataInfo(
            accessed=True,
            content_type="text/html",
            response_code=HTTPStatus.OK,
            error_message=None
        ),
        expected_result=ExpectedResult(
            has_html=True,  # Test for both compressed HTML and content metadata
            scrape_status=ScrapeStatus.SUCCESS
        )
    ),
    # URLs that give 404s should be updated with the appropriate scrape status
    #  and their web metadata status should be updated to 404
    TestURLHTMLTaskSetupEntry(
        url_info=TestURLInfo(
            url="https://not-found-path.com/submitted",
            status=URLStatus.ERROR
        ),
        web_metadata_info=TestWebMetadataInfo(
            accessed=True,
            content_type="text/html",
            response_code=HTTPStatus.OK,
            error_message=None
        ),
        give_error=TestErrorType.HTTP_404,
        expected_result=ExpectedResult(
            has_html=False,
            scrape_status=ScrapeStatus.ERROR,
            web_metadata_status_marked_404=True
        )
    ),
    # URLs that give errors should be updated with the appropriate scrape status
    TestURLHTMLTaskSetupEntry(
        url_info=TestURLInfo(
            url="https://error-path.com/submitted",
            status=URLStatus.ERROR
        ),
        web_metadata_info=TestWebMetadataInfo(
            accessed=True,
            content_type="text/html",
            response_code=HTTPStatus.OK,
            error_message=None
        ),
        give_error=TestErrorType.SCRAPER,
        expected_result=ExpectedResult(
            has_html=False,
            scrape_status=ScrapeStatus.ERROR
        )
    ),
    # URLs with non-200 web metadata should not be processed
    TestURLHTMLTaskSetupEntry(
        url_info=TestURLInfo(
            url="https://not-200-path.com/submitted",
            status=URLStatus.PENDING
        ),
        web_metadata_info=TestWebMetadataInfo(
            accessed=True,
            content_type="text/html",
            response_code=HTTPStatus.PERMANENT_REDIRECT,
            error_message=None
        ),
        expected_result=ExpectedResult(
            has_html=False,
            scrape_status=None
        )
    ),
    # URLs with no web metadata should not be processed
    TestURLHTMLTaskSetupEntry(
        url_info=TestURLInfo(
            url="https://no-web-metadata.com/submitted",
            status=URLStatus.PENDING
        ),
        web_metadata_info=None,
        expected_result=ExpectedResult(
            has_html=False,
            scrape_status=None
        )
    )
]