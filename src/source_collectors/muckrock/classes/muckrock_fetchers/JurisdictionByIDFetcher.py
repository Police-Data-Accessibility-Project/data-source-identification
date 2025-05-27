from src.source_collectors.muckrock.classes.fetch_requests.FetchRequestBase import FetchRequest
from src.source_collectors.muckrock.classes.muckrock_fetchers.MuckrockFetcher import MuckrockFetcher
from src.source_collectors.muckrock.constants import BASE_MUCKROCK_URL


class JurisdictionByIDFetchRequest(FetchRequest):
    jurisdiction_id: int

class JurisdictionByIDFetcher(MuckrockFetcher):

    def build_url(self, request: JurisdictionByIDFetchRequest) -> str:
        return f"{BASE_MUCKROCK_URL}/jurisdiction/{request.jurisdiction_id}/"

    async def get_jurisdiction(self, jurisdiction_id: int) -> dict:
        return await self.fetch(request=JurisdictionByIDFetchRequest(jurisdiction_id=jurisdiction_id))
