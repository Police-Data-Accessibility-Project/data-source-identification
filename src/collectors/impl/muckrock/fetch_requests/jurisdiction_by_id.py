from src.collectors.impl.muckrock.fetch_requests.base import FetchRequest


class JurisdictionByIDFetchRequest(FetchRequest):
    jurisdiction_id: int
