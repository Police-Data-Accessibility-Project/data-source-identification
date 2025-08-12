from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.queries.insert.urls.request_manager import InsertURLsRequestManager
from src.util.clean import clean_url
from src.db.dtos.url.insert import InsertURLsInfo
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.duplicate.pydantic.insert import DuplicateInsertInfo
from src.db.models.impl.url.core.pydantic.info import URLInfo
from src.db.queries.base.builder import QueryBuilderBase


class InsertURLsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_infos: list[URLInfo],
        batch_id: int
    ):
        super().__init__()
        self.url_infos = url_infos
        self.batch_id = batch_id

    async def run(self, session: AsyncSession) -> InsertURLsInfo:
        url_mappings = []
        duplicates = []
        rm = InsertURLsRequestManager(session=session)
        for url_info in self.url_infos:
            url_info.url = clean_url(url_info.url)
            url_info.batch_id = self.batch_id
            try:
                async with session.begin_nested() as sp:
                    url_id = await rm.insert_url(url_info)
                    url_mappings.append(
                        URLMapping(
                            url_id=url_id,
                            url=url_info.url
                        )
                    )
            except IntegrityError:
                sp.rollback()
                orig_url_info = await rm.get_url_info_by_url(url_info.url)
                duplicate_info = DuplicateInsertInfo(
                    batch_id=self.batch_id,
                    original_url_id=orig_url_info.id
                )
                duplicates.append(duplicate_info)
        await rm.insert_duplicates(duplicates)

        return InsertURLsInfo(
            url_mappings=url_mappings,
            total_count=len(self.url_infos),
            original_count=len(url_mappings),
            duplicate_count=len(duplicates),
            url_ids=[url_mapping.url_id for url_mapping in url_mappings]
        )
