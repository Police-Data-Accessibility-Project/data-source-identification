from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.collectors.enums import URLStatus
from src.core.tasks.url.operators.submit_approved_url.tdo import SubmitApprovedURLTDO
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh

class GetValidatedURLsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[SubmitApprovedURLTDO]:
        query = await self._build_query()
        urls = await sh.scalars(session, query)
        return await self._process_results(urls)

    async def _process_results(self, urls):
        results: list[SubmitApprovedURLTDO] = []
        for url in urls:
            try:
                tdo = await self._process_result(url)
            except Exception as e:
                raise ValueError(f"Failed to process url {url.id}") from e
            results.append(tdo)
        return results

    @staticmethod
    async def _build_query():
        query = (
            select(URL)
            .where(URL.outcome == URLStatus.VALIDATED.value)
            .options(
                selectinload(URL.optional_data_source_metadata),
                selectinload(URL.confirmed_agencies),
                selectinload(URL.reviewing_user)
            ).limit(100)
        )
        return query

    @staticmethod
    async def _process_result(url: URL) -> SubmitApprovedURLTDO:
        agency_ids = []
        for agency in url.confirmed_agencies:
            agency_ids.append(agency.agency_id)
        optional_metadata = url.optional_data_source_metadata
        if optional_metadata is None:
            record_formats = None
            data_portal_type = None
            supplying_entity = None
        else:
            record_formats = optional_metadata.record_formats
            data_portal_type = optional_metadata.data_portal_type
            supplying_entity = optional_metadata.supplying_entity
        tdo = SubmitApprovedURLTDO(
            url_id=url.id,
            url=url.url,
            name=url.name,
            agency_ids=agency_ids,
            description=url.description,
            record_type=url.record_type,
            record_formats=record_formats,
            data_portal_type=data_portal_type,
            supplying_entity=supplying_entity,
            approving_user_id=url.reviewing_user.user_id
        )
        return tdo