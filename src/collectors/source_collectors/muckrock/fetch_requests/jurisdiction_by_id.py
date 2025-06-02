from src.collectors.source_collectors.muckrock.fetch_requests.base import FetchRequest


class JurisdictionByIDFetchRequest(FetchRequest):
    jurisdiction_id: int
