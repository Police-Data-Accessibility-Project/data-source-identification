from abc import ABC, abstractmethod
from time import sleep

import requests

from source_collectors.muckrock.muckrock_fetchers.MuckrockFetcher import FetchRequest


class MuckrockLoopFetcher(ABC):


    def __init__(self, initial_request: FetchRequest):
        self.initial_request = initial_request

    def loop_fetch(self):
        url = self.build_url(self.initial_request)
        while url is not None:
            response = requests.get(url)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(f"Failed to get records on request `{url}`: {e}")
                return None

            data = response.json()
            self.process_results(data["results"])
            self.report_progress()
            url = data["next"]
            sleep(1)

    @abstractmethod
    def process_results(self, results: list[dict]):
        pass

    @abstractmethod
    def build_url(self, request: FetchRequest) -> str:
        pass

    @abstractmethod
    def report_progress(self):
        pass
