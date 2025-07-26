from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.sync.data_sources.queries.upsert.agency.query import URLAgencyLinkUpdateQueryBuilder
from src.core.tasks.scheduled.sync.data_sources.queries.upsert.agency.params import UpdateLinkURLAgencyForDataSourcesSyncParams


async def update_agency_links(
    session: AsyncSession,
    params: list[UpdateLinkURLAgencyForDataSourcesSyncParams]
) -> None:
    """Overwrite existing url_agency links with new ones, if applicable."""
    query = URLAgencyLinkUpdateQueryBuilder(params)
    await query.run(session)