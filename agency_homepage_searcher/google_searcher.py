from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import os


class GoogleSearcher:

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("CUSTOM_SEARCH_API_KEY")
        self.cse_id = os.getenv("CUSTOM_SEARCH_ENGINE_ID")
        # Check if api key and cse id are set
        if self.api_key is None or self.cse_id is None:
            raise RuntimeError("Custom search API key and CSE ID must be set in .env file")

        self.service = build("customsearch", "v1", developerKey=self.api_key)

    def search(self, query: str) -> list[dict]:
        try:
            res = self.service.cse().list(q=query, cx=self.cse_id).execute()
            return res['items']
            # Process your results
        except HttpError as e:
            if e.resp.status == 403:
                raise RuntimeError(f"Quota exceeded for the day. Original Error: {e}")
            else:
                raise RuntimeError(f"An error occurred: {e}")
