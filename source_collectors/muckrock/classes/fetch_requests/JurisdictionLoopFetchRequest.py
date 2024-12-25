from source_collectors.muckrock.classes.fetch_requests.FetchRequestBase import FetchRequest


class JurisdictionLoopFetchRequest(FetchRequest):
    level: str
    parent: int
    town_names: list
