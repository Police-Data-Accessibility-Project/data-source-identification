from source_collectors.muckrock.classes.fetch_requests.FetchRequestBase import FetchRequest
from source_collectors.muckrock.classes.muckrock_fetchers.MuckrockFetcher import MuckrockFetcher
from source_collectors.muckrock.constants import BASE_MUCKROCK_URL

FOIA_BASE_URL = f"{BASE_MUCKROCK_URL}/foia"


class FOIAFetchRequest(FetchRequest):
    page: int
    page_size: int


class FOIAFetcher(MuckrockFetcher):
    """
    A fetcher for FOIA requests.
    Iterates through all FOIA requests available through the MuckRock FOIA API.
    """

    def __init__(self, start_page: int = 1, per_page: int = 100):
        """
        Constructor for the FOIAFetcher class.

        Args:
            start_page (int): The page number to start fetching from (default is 1).
            per_page (int): The number of results to fetch per page (default is 100).
        """
        self.current_page = start_page
        self.per_page = per_page

    def build_url(self, request: FOIAFetchRequest) -> str:
        return f"{FOIA_BASE_URL}?page={request.page}&page_size={request.page_size}&format=json"

    async def fetch_next_page(self) -> dict | None:
        """
        Fetches data from a specific page of the MuckRock FOIA API.
        """
        page = self.current_page
        self.current_page += 1
        request = FOIAFetchRequest(page=page, page_size=self.per_page)
        return await self.fetch(request)

