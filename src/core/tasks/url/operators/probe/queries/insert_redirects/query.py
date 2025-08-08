from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.probe.queries.insert_redirects.convert import \
    convert_url_response_mapping_to_web_metadata_list, convert_to_url_mappings, convert_to_url_insert_models
from src.core.tasks.url.operators.probe.queries.insert_redirects.extract import extract_response_pairs
from src.core.tasks.url.operators.probe.queries.insert_redirects.models.url_response_map import URLResponseMapping
from src.core.tasks.url.operators.probe.queries.urls.exist.model import UrlExistsResult
from src.core.tasks.url.operators.probe.queries.urls.exist.query import URLsExistInDBQueryBuilder
from src.core.tasks.url.operators.probe.tdo import URLProbeTDO
from src.db.dtos.url.mapping import URLMapping
from src.db.helpers.session import session_helper as sh
from src.db.models.instantiations.link.url_redirect_url.pydantic import LinkURLRedirectURLPydantic
from src.db.models.instantiations.url.web_metadata.insert import URLWebMetadataPydantic
from src.db.queries.base.builder import QueryBuilderBase
from src.external.url_request.probe.models.response import URLProbeResponse
from src.util.url_mapper import URLMapper


class InsertRedirectsQueryBuilder(QueryBuilderBase):
    def __init__(
        self,
        tdos: list[URLProbeTDO],
    ):
        super().__init__()
        self.tdos = tdos
        self.source_url_mappings = [tdo.url_mapping for tdo in self.tdos]
        self._mapper = URLMapper(self.source_url_mappings)

        self._response_pairs = extract_response_pairs(self.tdos)

        self._source_probe_responses: list[URLProbeResponse] = [
            pair.source
            for pair in self._response_pairs
        ]
        self._destination_probe_responses: list[URLProbeResponse] = [
            pair.destination
            for pair in self._response_pairs
        ]
        self._destination_urls: list[str] = [
            response.url
            for response in self._destination_probe_responses
        ]

        self._source_url_to_id_mapping: dict[str, int] = {
            url_mapping.url: url_mapping.url_id
            for url_mapping in self.source_url_mappings
        }
        self._destination_url_to_probe_response_mapping: dict[str, URLProbeResponse] = {
            response.url: response
            for response in self._destination_probe_responses
        }




    async def run(self, session: AsyncSession) -> None:
        """
        Modifies:
            self._mapper
        """

        # TODO: Extant destination URLs might need web metadata. Upsert?

        all_dest_url_mappings = await self._get_all_dest_url_mappings(session)
        self._mapper.add_mappings(all_dest_url_mappings)
        await self._add_web_metadata(session, all_dest_url_mappings=all_dest_url_mappings)
        await self._add_redirect_links(session)


    async def _get_all_dest_url_mappings(
        self,
        session: AsyncSession
    ) -> list[URLMapping]:
        extant_destination_mappings: list[URLMapping] = await self._get_extant_destination_url_mappings(session)
        extant_destination_urls: set[str] = set([url_mapping.url for url_mapping in extant_destination_mappings])
        new_dest_urls: list[str] = [
            url
            for url in self._destination_urls
            if url not in extant_destination_urls
        ]
        new_dest_url_mappings: list[URLMapping] = await self._insert_new_destination_urls(
            session, urls=new_dest_urls
        )
        all_dest_url_mappings: list[URLMapping] = extant_destination_mappings + new_dest_url_mappings
        return all_dest_url_mappings

    async def _add_web_metadata(self, session: AsyncSession, all_dest_url_mappings: list[URLMapping]):
        dest_url_response_mappings: list[URLResponseMapping] = await self._build_destination_url_response_mappings(
            all_dest_url_mappings
        )
        source_url_response_mappings: list[URLResponseMapping] = self._build_source_url_response_mappings()
        all_url_response_mappings: list[URLResponseMapping] = source_url_response_mappings + dest_url_response_mappings
        web_metadata_list: list[URLWebMetadataPydantic] = convert_url_response_mapping_to_web_metadata_list(
            all_url_response_mappings
        )
        await sh.bulk_upsert(session, models=web_metadata_list)


    async def _get_extant_destination_url_mappings(self, session: AsyncSession) -> list[URLMapping]:
        results: list[UrlExistsResult] = await URLsExistInDBQueryBuilder(
            urls=self._destination_urls
        ).run(session)
        extant_urls = [result for result in results if result.exists]
        return convert_to_url_mappings(extant_urls)

    async def _insert_new_destination_urls(
        self,
        session: AsyncSession,
        urls: list[str]
    ) -> list[URLMapping]:
        if len(urls) == 0:
            return []
        insert_models = convert_to_url_insert_models(urls)
        url_ids = await sh.bulk_insert(session, models=insert_models, return_ids=True)
        url_mappings = [
            URLMapping(url=url, url_id=url_id)
            for url, url_id
            in zip(urls, url_ids)
        ]
        return url_mappings

    async def _build_destination_url_response_mappings(
        self,
        destination_url_mappings: list[URLMapping]
    ) -> list[URLResponseMapping]:
        results = []
        for url_mapping in destination_url_mappings:
            response = self._destination_url_to_probe_response_mapping[url_mapping.url]
            results.append(URLResponseMapping(url_mapping=url_mapping, response=response))
        return results

    def _build_source_url_response_mappings(self) -> list[URLResponseMapping]:
        results = []
        for tdo in self.tdos:
            results.append(
                URLResponseMapping(
                    url_mapping=tdo.url_mapping,
                    response=tdo.response.response.source
                )
            )
        return results

    async def _add_redirect_links(self, session: AsyncSession):
        links: list[LinkURLRedirectURLPydantic] = []
        for pair in self._response_pairs:
            source_url_id = self._mapper.get_id(pair.source.url)
            destination_url_id = self._mapper.get_id(pair.destination.url)
            link = LinkURLRedirectURLPydantic(
                source_url_id=source_url_id,
                destination_url_id=destination_url_id
            )
            links.append(link)
        await sh.bulk_insert(session, models=links)
