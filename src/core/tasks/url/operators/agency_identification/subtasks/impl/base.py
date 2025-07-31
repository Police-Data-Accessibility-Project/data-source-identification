import abc
from abc import ABC
from typing import Optional

from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo


class AgencyIdentificationSubtaskBase(ABC):

    @abc.abstractmethod
    async def run(
            self,
            url_id: int,
            collector_metadata: dict | None = None
    ) -> list[URLAgencySuggestionInfo]:
        raise NotImplementedError
