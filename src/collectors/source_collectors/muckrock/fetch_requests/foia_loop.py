from src.collectors.source_collectors.muckrock.fetch_requests.base import FetchRequest


class FOIALoopFetchRequest(FetchRequest):
    jurisdiction: int
