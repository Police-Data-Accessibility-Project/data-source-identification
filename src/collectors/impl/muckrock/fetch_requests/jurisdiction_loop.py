from src.collectors.impl.muckrock.fetch_requests.base import FetchRequest


class JurisdictionLoopFetchRequest(FetchRequest):
    level: str
    parent: int
    town_names: list
