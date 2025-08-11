from src.collectors.impl.muckrock.fetch_requests.base import FetchRequest


class FOIAFetchRequest(FetchRequest):
    page: int
    page_size: int
