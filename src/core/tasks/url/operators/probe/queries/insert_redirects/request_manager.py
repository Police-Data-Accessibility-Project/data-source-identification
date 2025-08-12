from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.probe.queries.insert_redirects.convert import convert_to_url_mappings, \
    convert_to_url_insert_models, convert_tdo_to_url_response_mappings, \
    convert_url_response_mapping_to_web_metadata_list
from src.core.tasks.url.operators.probe.queries.insert_redirects.map import map_url_mappings_to_probe_responses
from src.core.tasks.url.operators.probe.queries.insert_redirects.models.url_response_map import URLResponseMapping
from src.core.tasks.url.operators.probe.queries.urls.exist.model import UrlExistsResult
from src.core.tasks.url.operators.probe.queries.urls.exist.query import URLsExistInDBQueryBuilder
from src.core.tasks.url.operators.probe.tdo import URLProbeTDO
from src.db.dtos.url.mapping import URLMapping
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.link.url_redirect_url.pydantic import LinkURLRedirectURLPydantic
from src.db.models.impl.url.web_metadata.insert import URLWebMetadataPydantic
from src.external.url_request.probe.models.redirect import URLProbeRedirectResponsePair
from src.external.url_request.probe.models.response import URLProbeResponse
from src.util.url_mapper import URLMapper


class InsertRedirectsRequestManager:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_url_mappings_in_db(
        self,
        urls: list[str],
    ):
        results: list[UrlExistsResult] = await URLsExistInDBQueryBuilder(
            urls=urls
        ).run(self.session)
        extant_urls = [result for result in results if result.exists]
        return convert_to_url_mappings(extant_urls)

    async def insert_new_urls(self, urls: list[str]) -> list[URLMapping]:
        if len(urls) == 0:
            return []
        deduplicated_urls = list(set(urls))
        insert_models = convert_to_url_insert_models(deduplicated_urls)
        url_ids = await sh.bulk_insert(self.session, models=insert_models, return_ids=True)
        url_mappings = [
            URLMapping(url=url, url_id=url_id)
            for url, url_id
            in zip(deduplicated_urls, url_ids)
        ]
        return url_mappings

    async def add_web_metadata(
        self,
        all_dest_url_mappings: list[URLMapping],
        dest_url_to_probe_response_mappings: dict[str, URLProbeResponse],
        tdos: list[URLProbeTDO],
    ) -> None:
        dest_url_response_mappings = map_url_mappings_to_probe_responses(
            url_mappings=all_dest_url_mappings,
            url_to_probe_responses=dest_url_to_probe_response_mappings
        )
        src_url_response_mappings: list[URLResponseMapping] = convert_tdo_to_url_response_mappings(
            tdos=tdos
        )
        all_url_response_mappings: list[URLResponseMapping] = src_url_response_mappings + dest_url_response_mappings
        web_metadata_list: list[URLWebMetadataPydantic] = convert_url_response_mapping_to_web_metadata_list(
            all_url_response_mappings
        )
        await sh.bulk_upsert(self.session, models=web_metadata_list)

    async def add_redirect_links(
        self,
        response_pairs: list[URLProbeRedirectResponsePair],
        mapper: URLMapper
    ) -> None:
        links: list[LinkURLRedirectURLPydantic] = []
        for pair in response_pairs:
            source_url_id = mapper.get_id(pair.source.url)
            destination_url_id = mapper.get_id(pair.destination.url)
            link = LinkURLRedirectURLPydantic(
                source_url_id=source_url_id,
                destination_url_id=destination_url_id
            )
            links.append(link)
        await sh.bulk_insert(self.session, models=links)
