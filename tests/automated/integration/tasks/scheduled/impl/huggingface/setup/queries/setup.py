from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.utils.compression import compress_html
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.models.entry import \
    TestPushToHuggingFaceURLSetupEntry as Entry
from tests.automated.integration.tasks.scheduled.impl.huggingface.setup.models.record import \
    TestPushToHuggingFaceRecordSetupRecord as Record


class SetupTestPushToHuggingFaceEntryQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        entries: list[Entry]
    ):
        super().__init__()
        self.entries = entries

    async def run(self, session: AsyncSession) -> list[Record]:
        records = []
        for idx, entry in enumerate(self.entries):
            if idx % 2 == 0:
                name = "Test Push to Hugging Face URL Setup Entry"
                description = "This is a test push to Hugging Face URL setup entry"
            else:
                name = None
                description = None
            inp = entry.input
            url = URL(
                url=f"www.testPushToHuggingFaceURLSetupEntry.com/{idx}",
                status=inp.status,
                name=name,
                description=description,
                record_type=inp.record_type,
                source=URLSource.COLLECTOR
            )
            session.add(url)
            await session.flush()
            if entry.input.has_html_content:
                compressed_html = URLCompressedHTML(
                    url_id=url.id,
                    compressed_html=compress_html(f"<html><div>Test Push to Hugging Face URL Setup Entry {idx}</div></html>"),
                )
                session.add(compressed_html)
            record = Record(
                url_id=url.id,
                expected_output=entry.expected_output,
                record_type_fine=inp.record_type
            )
            records.append(record)

        return records

