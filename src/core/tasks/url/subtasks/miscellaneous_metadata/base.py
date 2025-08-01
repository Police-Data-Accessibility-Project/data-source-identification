from abc import ABC, abstractmethod

from src.core.tasks.url.operators.misc_metadata.tdo import URLMiscellaneousMetadataTDO


class MiscellaneousMetadataSubtaskBase(ABC):

    @abstractmethod
    def process(self, tdo: URLMiscellaneousMetadataTDO):
        raise NotImplementedError