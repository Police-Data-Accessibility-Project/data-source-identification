from abc import ABC, abstractmethod

import requests

from source_collectors.muckrock.classes.fetch_requests.FetchRequestBase import FetchRequest
from source_collectors.muckrock.classes.exceptions.RequestFailureException import RequestFailureException


class MuckrockIterFetcherBase(ABC):

    def __init__(self, initial_request: FetchRequest):
        self.initial_request = initial_request

    def get_response(self, url) -> dict:
        # TODO: POINT OF MOCK
        response = requests.get(url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Failed to get records on request `{url}`: {e}")
            raise RequestFailureException
        return response.json()

    @abstractmethod
    def process_results(self, results: list[dict]):
        pass

    @abstractmethod
    def build_url(self, request: FetchRequest) -> str:
        pass
