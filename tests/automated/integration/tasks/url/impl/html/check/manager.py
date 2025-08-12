from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.scrape_info.sqlalchemy import URLScrapeInfo
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from tests.automated.integration.tasks.url.impl.html.setup.models.record import TestURLHTMLTaskSetupRecord


class TestURLHTMLTaskCheckManager:

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        records: list[TestURLHTMLTaskSetupRecord]
    ):
        self.adb_client = adb_client
        self.records = records
        self._id_to_entry = {record.url_id: record.entry for record in records}

    async def check(self):
        await self._check_has_html()
        await self._check_scrape_status()
        await self._check_has_same_url_status()
        await self._check_marked_as_404()

    async def _check_has_html(self) -> None:
        urls_with_html = [
            record.url_id
            for record in self.records
            if record.entry.expected_result.has_html
        ]

        compressed_html_list: list[URLCompressedHTML] = await self.adb_client.get_all(URLCompressedHTML)
        assert len(compressed_html_list) == len(urls_with_html)
        for compressed_html in compressed_html_list:
            assert compressed_html.url_id in urls_with_html

    async def _check_scrape_status(self) -> None:
        urls_with_scrape_status = [
            record.url_id
            for record in self.records
            if record.entry.expected_result.scrape_status is not None
        ]

        url_scrape_info_list: list[URLScrapeInfo] = await self.adb_client.get_all(URLScrapeInfo)
        assert len(url_scrape_info_list) == len(urls_with_scrape_status)
        for url_scrape_info in url_scrape_info_list:
            assert url_scrape_info.url_id in urls_with_scrape_status
            entry = self._id_to_entry[url_scrape_info.url_id]
            expected_scrape_status = entry.expected_result.scrape_status
            assert url_scrape_info.status == expected_scrape_status

    async def _check_has_same_url_status(self):
        urls: list[URL] = await self.adb_client.get_all(URL)
        for url in urls:
            entry = self._id_to_entry[url.id]
            if entry.expected_result.web_metadata_status_marked_404:
                continue
            assert url.status == entry.url_info.status, f"URL {url.url} has outcome {url.status} instead of {entry.url_info.status}"

    async def _check_marked_as_404(self):
        web_metadata_list: list[URLWebMetadata] = await self.adb_client.get_all(
            URLWebMetadata
        )
        for web_metadata in web_metadata_list:
            entry = self._id_to_entry[web_metadata.url_id]
            if entry.expected_result.web_metadata_status_marked_404:
                assert web_metadata.status_code == 404, f"URL {entry.url_info.url} has status code {web_metadata.status_code} instead of 404"
