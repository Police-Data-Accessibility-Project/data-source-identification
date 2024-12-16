from source_collectors.muckrock.constants import BASE_MUCKROCK_URL
from source_collectors.muckrock.muckrock_fetchers.MuckrockFetcher import FetchRequest, MuckrockFetcher


class AgencyFetchRequest(FetchRequest):
    agency_id: int

class AgencyFetcher(MuckrockFetcher):

    def build_url(self, request: AgencyFetchRequest) -> str:
        return f"{BASE_MUCKROCK_URL}/agency/{request.agency_id}/"

    def get_agency(self, agency_id: int):
        return self.fetch(AgencyFetchRequest(agency_id=agency_id))