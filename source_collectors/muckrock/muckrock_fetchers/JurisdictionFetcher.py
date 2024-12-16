from source_collectors.muckrock.constants import BASE_MUCKROCK_URL
from source_collectors.muckrock.muckrock_fetchers.MuckrockFetcher import FetchRequest, MuckrockFetcher


class JurisdictionFetchRequest(FetchRequest):
    jurisdiction_id: int

class JurisdictionFetcher(MuckrockFetcher):

    def build_url(self, request: JurisdictionFetchRequest) -> str:
        return f"{BASE_MUCKROCK_URL}/jurisdiction/{request.jurisdiction_id}/"

    def get_jurisdiction(self, jurisdiction_id: int) -> dict:
        return self.fetch(request=JurisdictionFetchRequest(jurisdiction_id=jurisdiction_id))
