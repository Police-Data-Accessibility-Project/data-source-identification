import abc
from abc import ABC
from dataclasses import dataclass

import requests
from pydantic import BaseModel


class FetchRequest(BaseModel):
    pass

class MuckrockFetcher(ABC):

    def fetch(self, request: FetchRequest):
        url = self.build_url(request)
        response = requests.get(url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Failed to get records on request `{url}`: {e}")
            return None

        return response.json()

    @abc.abstractmethod
    def build_url(self, request: FetchRequest) -> str:
        pass

