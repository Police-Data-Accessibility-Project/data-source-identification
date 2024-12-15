import requests

from source_collectors.muckrock.constants import BASE_MUCKROCK_URL

FOIA_BASE_URL = f"{BASE_MUCKROCK_URL}/foia"

class FOIAFetcher:

    def __init__(self, start_page: int = 1, per_page: int = 100):
        """
        Constructor for the FOIAFetcher class.

        Args:
            start_page (int): The page number to start fetching from (default is 1).
            per_page (int): The number of results to fetch per page (default is 100).
        """
        self.current_page = start_page
        self.per_page = per_page

    def fetch_next_page(self) -> dict | None:
        """
        Fetches data from a specific page of the MuckRock FOIA API.
        """
        page = self.current_page
        self.current_page += 1
        response = requests.get(
            FOIA_BASE_URL, params={"page": page, "page_size": self.per_page, "format": "json"}
        )
        if response.status_code == 200:
            return response.json()
        # TODO: Look into raising error instead of returning None
        print(f"Error fetching page {page}: {response.status_code}")
        return None

