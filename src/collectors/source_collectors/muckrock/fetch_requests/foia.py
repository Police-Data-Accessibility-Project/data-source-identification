from src.collectors.source_collectors.muckrock.fetch_requests.base import FetchRequest


class FOIAFetchRequest(FetchRequest):
    page: int
    page_size: int
