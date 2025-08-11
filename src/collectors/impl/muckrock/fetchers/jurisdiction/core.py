from src.collectors.impl.muckrock.fetch_requests.jurisdiction_by_id import \
    JurisdictionByIDFetchRequest
from src.collectors.impl.muckrock.fetchers.templates.fetcher import MuckrockFetcherBase
from src.collectors.impl.muckrock.constants import BASE_MUCKROCK_URL


class JurisdictionByIDFetcher(MuckrockFetcherBase):

    def build_url(self, request: JurisdictionByIDFetchRequest) -> str:
        return f"{BASE_MUCKROCK_URL}/jurisdiction/{request.jurisdiction_id}/"

    async def get_jurisdiction(self, jurisdiction_id: int) -> dict:
        return await self.fetch(request=JurisdictionByIDFetchRequest(jurisdiction_id=jurisdiction_id))
