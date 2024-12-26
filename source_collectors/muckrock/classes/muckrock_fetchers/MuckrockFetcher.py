import abc
from abc import ABC

import requests

from source_collectors.muckrock.classes.fetch_requests.FetchRequestBase import FetchRequest


class MuckrockNoMoreDataError(Exception):
    pass

class MuckrockServerError(Exception):
    pass


class MuckrockFetcher(ABC):

    def fetch(self, request: FetchRequest):
        url = self.build_url(request)
        response = requests.get(url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Failed to get records on request `{url}`: {e}")
            # If code is 404, raise NoMoreData error
            if e.response.status_code == 404:
                raise MuckrockNoMoreDataError
            if 500 <= e.response.status_code < 600:
                raise MuckrockServerError




            return None

        return response.json()

    @abc.abstractmethod
    def build_url(self, request: FetchRequest) -> str:
        pass

