from typing import Union

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import os

class GoogleSearcher:

    def __init__(
            self,
            api_key: str,
            cse_id: str
    ):
        load_dotenv()
        if api_key is None or cse_id is None:
            raise RuntimeError("Custom search API key and CSE ID required")
        self.api_key = api_key
        self.cse_id = cse_id

        self.service = build("customsearch", "v1", developerKey=self.api_key)

    def search(self, query: str) -> Union[list[dict], None]:
        try:
            res = self.service.cse().list(q=query, cx=self.cse_id).execute()
            return res['items']
            # Process your results
        except HttpError as e:
            if "Quota exceeded" in str(e):
                print("Quota exceeded for the day")
                return None
            else:
                raise RuntimeError(f"An error occurred: {e}")
