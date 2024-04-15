from dataclasses import dataclass
from typing import Union

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class QuotaExceededError(Exception):
    pass


"""
TODO: Update this so that it returns:
    url
    Title
    Snippet (if available)
Create Dataclass to contain all this stuff if necessary. 
"""


@dataclass
class GoogleSearchResult:
    url: str
    title: str
    snippet: str


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

    def call_google_search(self, query: str) -> dict:
        """
        Directly calls the Google Custom Search API with the provided query string
        Args:
            query: The search query that will be sent to Google.

        Returns:
            dict: The result of the Google search in dictionary format.

        """
        return self.service.cse().list(q=query, cx=self.cse_id).execute()

    def search(self, query: str) -> Union[list[GoogleSearchResult], None]:
        """
        Searches for results using the specified query.

        Args:
            query (str): The query to search for.

        Returns: Union[list[dict], None]: A list of dictionaries representing the search results.
            If the daily quota is exceeded, None is returned.
        """
        try:
            res = self.call_google_search(query)
            if "items" not in res:
                return None
            search_results = []
            for item in res['items']:
                search_result = GoogleSearchResult(
                    url=item['link'],
                    title=item['title'],
                    snippet=item.get('snippet', '')
                )
                search_results.append(search_result)
            return search_results
            # Process your results
        except HttpError as e:
            if "Quota exceeded" in str(e):
                raise QuotaExceededError("Quota exceeded for the day")
            else:
                raise RuntimeError(f"An error occurred: {str(e)}")