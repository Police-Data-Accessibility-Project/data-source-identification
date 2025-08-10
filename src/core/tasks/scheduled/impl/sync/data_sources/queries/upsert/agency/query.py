from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.agency.convert import convert_to_link_url_agency_models
from src.db.helpers.session import session_helper as sh
from src.db.models.instantiations.link.url_agency.pydantic import LinkURLAgencyPydantic
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.agency.params import UpdateLinkURLAgencyForDataSourcesSyncParams
from src.db.models.instantiations.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.queries.base.builder import QueryBuilderBase


class URLAgencyLinkUpdateQueryBuilder(QueryBuilderBase):
    """Given a set of URL-Agency links, remove all non-matching links and add new ones."""


    def __init__(self, models: list[UpdateLinkURLAgencyForDataSourcesSyncParams]):
        super().__init__()
        self.models = models
        self._new_links: dict[int, list[int]] = {
            model.url_id: model.new_agency_ids
            for model in self.models
        }
        self._existing_links: dict[int, list[int]] = defaultdict(list)
        self.existing_url_ids = {model.url_id for model in self.models}

    async def _get_existing_links(self, session: AsyncSession):
        """Get existing agency links for provided URLs.

        Modifies:
            self._existing_links
        """
        query = (
            select(LinkURLAgency)
            .where(
                LinkURLAgency.url_id.in_(
                    self.existing_url_ids
                )
            )
        )
        links = await session.scalars(query)
        for link in links:
            self._existing_links[link.url_id].append(link.agency_id)

    async def _update_links(self, session: AsyncSession):
        # Remove all existing links not in new links
        links_to_delete: list[LinkURLAgencyPydantic] = []
        links_to_insert: list[LinkURLAgencyPydantic] = []

        for url_id in self.existing_url_ids:
            new_agency_ids = self._new_links.get(url_id, [])
            existing_agency_ids = self._existing_links.get(url_id, [])
            # IDs to delete are existing agency ids that are not new agency ids
            ids_to_delete = set(existing_agency_ids) - set(new_agency_ids)
            # IDs to insert are new agency ids that are not existing agency ids
            ids_to_insert = set(new_agency_ids) - set(existing_agency_ids)

            links_to_delete.extend(
                convert_to_link_url_agency_models(
                    url_id=url_id,
                    agency_ids=list(ids_to_delete)
                )
            )
            links_to_insert.extend(
                convert_to_link_url_agency_models(
                    url_id=url_id,
                    agency_ids=list(ids_to_insert)
                )
            )

        await sh.bulk_delete(session=session, models=links_to_delete)
        await sh.bulk_insert(session=session, models=links_to_insert)

    async def run(self, session: AsyncSession):
        await self._get_existing_links(session=session)
        await self._update_links(session=session)


