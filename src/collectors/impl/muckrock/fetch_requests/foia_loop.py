from src.collectors.impl.muckrock.fetch_requests.base import FetchRequest


class FOIALoopFetchRequest(FetchRequest):
    jurisdiction: int
