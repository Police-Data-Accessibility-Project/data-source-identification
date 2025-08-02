from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.helpers.session import session_helper as sh
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.queries.base.builder import QueryBuilderBase
from tests.automated.integration.tasks.url.probe.setup.data import SETUP_ENTRIES
from tests.automated.integration.tasks.url.probe.setup.format import build_url_to_entry_map
from tests.automated.integration.tasks.url.probe.setup.models.entry import TestURLProbeTaskEntry


class CheckURLsInDBForURLProbeTaskQueryBuilder(QueryBuilderBase):

    def __init__(self):
        super().__init__()
        self._entries = SETUP_ENTRIES
        self._url_to_entry_map: dict[
            str, TestURLProbeTaskEntry
        ] = build_url_to_entry_map()

    async def run(self, session: AsyncSession) -> None:

        query = (
            select(
                URL.url,
                URLWebMetadata.accessed,
                URLWebMetadata.status_code,
                URLWebMetadata.content_type,
                URLWebMetadata.error_message
            )
            .join(URLWebMetadata, URL.id == URLWebMetadata.url_id)
        )
        mappings = await sh.mappings(session, query=query)
        assert len(mappings) == len(self._entries)
        for mapping in mappings:
            url = mapping["url"]
            entry = self._url_to_entry_map[url]
            assert entry.expected_accessed == mapping["accessed"]
            assert entry.url_probe_response.status_code == mapping["status_code"]
            assert entry.url_probe_response.content_type == mapping["content_type"]
            assert entry.url_probe_response.error == mapping["error_message"]

