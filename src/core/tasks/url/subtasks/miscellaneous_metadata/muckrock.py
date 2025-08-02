from src.core.tasks.url.operators.misc_metadata.tdo import URLMiscellaneousMetadataTDO
from src.core.tasks.url.subtasks.miscellaneous_metadata.base import \
    MiscellaneousMetadataSubtaskBase


class MuckrockMiscMetadataSubtask(MiscellaneousMetadataSubtaskBase):

    def process(self, tdo: URLMiscellaneousMetadataTDO):
        tdo.name = tdo.collector_metadata['title']
        tdo.description = tdo.collector_metadata['title']
