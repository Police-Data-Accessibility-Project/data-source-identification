from abc import ABC, abstractmethod

from core.DTOs.task_data_objects.URLMiscellaneousMetadataTDO import URLMiscellaneousMetadataTDO


class MiscellaneousMetadataSubtaskBase(ABC):

    @abstractmethod
    def process(self, tdo: URLMiscellaneousMetadataTDO):
        raise NotImplementedError