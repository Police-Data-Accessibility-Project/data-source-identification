from sqlalchemy import select

from src.collectors.enums import URLStatus
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.link.url_redirect_url.sqlalchemy import LinkURLRedirectURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata


class TestURLProbeCheckManager:

    def __init__(
        self,
        adb_client: AsyncDatabaseClient
    ):
        self.adb_client = adb_client

    async def check_url(
        self,
        url_id: int,
        expected_status: URLStatus
    ):
        url: URL = await self.adb_client.one_or_none(select(URL).where(URL.id == url_id))
        assert url is not None
        assert url.status == expected_status

    async def check_web_metadata(
        self,
        url_id: int,
        status_code: int | None,
        content_type: str | None,
        error: str | None,
        accessed: bool
    ):
        web_metadata: URLWebMetadata = await self.adb_client.one_or_none(
            select(URLWebMetadata).where(URLWebMetadata.url_id == url_id)
        )
        assert web_metadata is not None
        assert web_metadata.url_id == url_id
        assert web_metadata.status_code == status_code
        assert web_metadata.content_type == content_type
        assert web_metadata.error_message == error
        assert web_metadata.accessed == accessed

    async def check_redirect(
        self,
        source_url_id: int,
    ) -> int:
        """
        Check existence of redirect link using source_url_id and return destination_url_id
        """
        redirect: LinkURLRedirectURL = await self.adb_client.one_or_none(
            select(LinkURLRedirectURL).where(LinkURLRedirectURL.source_url_id == source_url_id)
        )
        assert redirect is not None
        return redirect.destination_url_id