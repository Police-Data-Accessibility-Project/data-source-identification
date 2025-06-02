from src.core.tasks.operators.url_miscellaneous_metadata.tdo import URLMiscellaneousMetadataTDO
from src.core.tasks.subtasks.miscellaneous_metadata.base import \
    MiscellaneousMetadataSubtaskBase


class AutoGooglerMiscMetadataSubtask(MiscellaneousMetadataSubtaskBase):

    def process(self, tdo: URLMiscellaneousMetadataTDO):
        tdo.name = tdo.collector_metadata['title']
        tdo.description = tdo.collector_metadata['snippet']