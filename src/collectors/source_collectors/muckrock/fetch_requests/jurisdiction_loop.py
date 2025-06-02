from src.collectors.source_collectors.muckrock.fetch_requests.base import FetchRequest


class JurisdictionLoopFetchRequest(FetchRequest):
    level: str
    parent: int
    town_names: list
