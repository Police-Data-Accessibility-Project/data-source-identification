from source_collectors.muckrock.constants import BASE_MUCKROCK_URL
from source_collectors.muckrock.classes.muckrock_fetchers.MuckrockFetcher import MuckrockFetcher
from source_collectors.muckrock.classes.fetch_requests.FetchRequestBase import FetchRequest


class AgencyFetchRequest(FetchRequest):
    agency_id: int

class AgencyFetcher(MuckrockFetcher):

    def build_url(self, request: AgencyFetchRequest) -> str:
        return f"{BASE_MUCKROCK_URL}/agency/{request.agency_id}/"

    def get_agency(self, agency_id: int):
        return self.fetch(AgencyFetchRequest(agency_id=agency_id))