from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.probe.queries.insert_redirects.extract import extract_response_pairs
from src.core.tasks.url.operators.probe.queries.insert_redirects.filter import filter_new_dest_urls
from src.core.tasks.url.operators.probe.queries.insert_redirects.request_manager import InsertRedirectsRequestManager
from src.core.tasks.url.operators.probe.tdo import URLProbeTDO
from src.db.dtos.url.mapping import URLMapping
from src.db.helpers.session import session_helper as sh
from src.db.models.instantiations.link.url_redirect_url.pydantic import LinkURLRedirectURLPydantic
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

        self._destination_probe_responses: list[URLProbeResponse] = [
            pair.destination
            for pair in self._response_pairs
        ]
        self._destination_urls: list[str] = [
            response.url
            for response in self._destination_probe_responses
        ]

        self._destination_url_to_probe_response_mapping: dict[str, URLProbeResponse] = {
            response.url: response
            for response in self._destination_probe_responses
        }




    async def run(self, session: AsyncSession) -> None:
        """
        Modifies:
            self._mapper
        """

        rm = InsertRedirectsRequestManager(
            session=session
        )

        dest_url_mappings_in_db: list[URLMapping] = await rm.get_url_mappings_in_db(
            urls=self._destination_urls
        )

        new_dest_urls: list[str] = filter_new_dest_urls(
            url_mappings_in_db=dest_url_mappings_in_db,
            all_dest_urls=self._destination_urls
        )
        new_dest_url_mappings: list[URLMapping] = await rm.insert_new_urls(
            urls=new_dest_urls
        )
        all_dest_url_mappings: list[URLMapping] = dest_url_mappings_in_db + new_dest_url_mappings

        self._mapper.add_mappings(all_dest_url_mappings)

        await rm.add_web_metadata(
            all_dest_url_mappings=all_dest_url_mappings,
            dest_url_to_probe_response_mappings=self._destination_url_to_probe_response_mapping,
            tdos=self.tdos
        )

        await rm.add_redirect_links(
            response_pairs=self._response_pairs,
            mapper=self._mapper
        )
