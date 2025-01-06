from typing import Union

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from source_collectors.auto_googler.DTOs import GoogleSearchQueryResultsInnerDTO


class QuotaExceededError(Exception):
    pass

class GoogleSearcher:
    """
    A class that provides a GoogleSearcher object for performing searches using the Google Custom Search API.

    Attributes:
        api_key (str): The API key required for accessing the Google Custom Search API.
        cse_id (str): The CSE (Custom Search Engine) ID required for identifying the specific search engine to use.
        service (Google API service): The Google API service object for performing the search.

    Methods:
        __init__(api_key: str, cse_id: str)
            Initializes a GoogleSearcher object with the provided API key and CSE ID. Raises a RuntimeError if either
            the API key or CSE ID is None.

        search(query: str) -> Union[list[dict], None]
            Performs a search using the Google Custom Search API with the provided query string. Returns a list of
            search results as dictionaries or None if the daily quota for the API has been exceeded. Raises a RuntimeError
            if any other error occurs during the search.
    """
    GOOGLE_SERVICE_NAME = "customsearch"
    GOOGLE_SERVICE_VERSION = "v1"

    def __init__(
            self,
            api_key: str,
            cse_id: str
    ):
        if api_key is None or cse_id is None:
            raise RuntimeError("Custom search API key and CSE ID cannot be None.")
        self.api_key = api_key
        self.cse_id = cse_id

        self.service = build(self.GOOGLE_SERVICE_NAME,
                             self.GOOGLE_SERVICE_VERSION,
                             developerKey=self.api_key)

    def search(self, query: str) -> Union[list[dict], None]:
        """
        Searches for results using the specified query.

        Args:
            query (str): The query to search for.

        Returns: Union[list[dict], None]: A list of dictionaries representing the search results.
            If the daily quota is exceeded, None is returned.
        """
        try:
            return self.get_query_results(query)
            # Process your results
        except HttpError as e:
            if "Quota exceeded" in str(e):
                raise QuotaExceededError("Quota exceeded for the day")
            else:
                raise RuntimeError(f"An error occurred: {str(e)}")

    def get_query_results(self, query) -> list[GoogleSearchQueryResultsInnerDTO] or None:
        results = self.service.cse().list(q=query, cx=self.cse_id).execute()
        if "items" not in results:
            return None
        items = []
        for item in results["items"]:
            inner_dto = GoogleSearchQueryResultsInnerDTO(
                url=item["link"],
                title=item["title"],
                snippet=item["snippet"]
            )
            items.append(inner_dto)

        return items
