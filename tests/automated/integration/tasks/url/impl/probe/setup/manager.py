from typing import cast, Literal

from src.collectors.enums import URLStatus
from src.core.tasks.url.operators.probe.core import URLProbeTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from src.external.url_request.core import URLRequestInterface
from src.external.url_request.probe.models.redirect import URLProbeRedirectResponsePair
from src.external.url_request.probe.models.response import URLProbeResponse
from src.external.url_request.probe.models.wrapper import URLProbeResponseOuterWrapper
from tests.automated.integration.tasks.url.impl.probe.constants import TEST_URL, TEST_DEST_URL, TEST_SOURCE
from tests.automated.integration.tasks.url.impl.probe.mocks.url_request_interface import MockURLRequestInterface


class TestURLProbeSetupManager:

    def __init__(
        self,
        adb_client: AsyncDatabaseClient
    ):
        self.adb_client = adb_client

    async def setup_url(
        self,
        url_status: URLStatus,
        url: str = TEST_URL
    ) -> int:
        url_insert_model = URLInsertModel(
            url=url,
            status=url_status,
            source=TEST_SOURCE
        )
        return (
            await self.adb_client.bulk_insert(
                models=[url_insert_model],
                return_ids=True
            )
        )[0]

    def setup_operator(
        self,
        response_or_responses: URLProbeResponseOuterWrapper | list[URLProbeResponseOuterWrapper]
    ) -> URLProbeTaskOperator:
        operator = URLProbeTaskOperator(
            adb_client=self.adb_client,
            url_request_interface=cast(
                URLRequestInterface,
                MockURLRequestInterface(
                    response_or_responses=response_or_responses
                )
            )
        )
        return operator

    @staticmethod
    def setup_no_redirect_probe_response(
        status_code: int | None,
        content_type: str | None,
        error: str | None,
        url: str = TEST_URL
    ) -> URLProbeResponseOuterWrapper:
        return URLProbeResponseOuterWrapper(
            original_url=url,
            response=URLProbeResponse(
                url=url,
                status_code=status_code,
                content_type=content_type,
                error=error
            )
        )

    @staticmethod
    def setup_redirect_probe_response(
        redirect_status_code: Literal[301, 302, 303, 307, 308],
        dest_status_code: int,
        dest_content_type: str | None,
        dest_error: str | None,
        source_url: str = TEST_URL,
        redirect_url: str = TEST_DEST_URL
    ) -> URLProbeResponseOuterWrapper:
        if redirect_status_code not in (301, 302, 303, 307, 308):
            raise ValueError('Redirect response must be one of 301, 302, 303, 307, 308')
        return URLProbeResponseOuterWrapper(
            original_url=source_url,
            response=URLProbeRedirectResponsePair(
                source=URLProbeResponse(
                    url=source_url,
                    status_code=redirect_status_code,
                    content_type=None,
                    error=None
                ),
                destination=URLProbeResponse(
                    url=redirect_url,
                    status_code=dest_status_code,
                    content_type=dest_content_type,
                    error=dest_error
                )
            )
        )

