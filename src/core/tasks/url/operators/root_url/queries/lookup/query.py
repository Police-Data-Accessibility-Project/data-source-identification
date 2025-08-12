from sqlalchemy import select, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.root_url.queries.lookup.response import LookupRootsURLResponse
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.flag.root_url.sqlalchemy import FlagRootURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class LookupRootURLsQueryBuilder(QueryBuilderBase):
    """
    Looks up URLs to see if they exist in the database as root URLs
    """

    def __init__(self, urls: list[str]):
        super().__init__()
        self.urls = urls

    async def run(self, session: AsyncSession) -> list[LookupRootsURLResponse]:

        # Run query
        query = select(
            URL.id,
            URL.url,
            case(
                (FlagRootURL.url_id.is_(None), False),
                else_=True
            ).label("flagged_as_root")
        ).outerjoin(FlagRootURL).where(
            URL.url.in_(self.urls),
        )
        mappings = await sh.mappings(session, query=query)

        # Store results in intermediate map
        url_to_response_map: dict[str, LookupRootsURLResponse] = {}
        for mapping in mappings:
            url = mapping["url"]
            response = LookupRootsURLResponse(
                url=url,
                url_id=mapping["id"],
                flagged_as_root=mapping["flagged_as_root"]
            )
            url_to_response_map[url] = response

        # Iterate through original URLs and add missing responses
        results: list[LookupRootsURLResponse] = []
        for url in self.urls:
            response = url_to_response_map.get(url)
            if response is None:
                response = LookupRootsURLResponse(
                    url=url,
                    url_id=None,
                    flagged_as_root=False
                )
            results.append(response)

        return results
