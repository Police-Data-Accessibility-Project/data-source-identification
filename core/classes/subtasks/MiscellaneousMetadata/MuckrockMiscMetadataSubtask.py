from core.DTOs.task_data_objects.URLMiscellaneousMetadataTDO import URLMiscellaneousMetadataTDO
from core.classes.subtasks.MiscellaneousMetadata.MiscellaneousMetadataSubtaskBase import \
    MiscellaneousMetadataSubtaskBase


class MuckrockMiscMetadataSubtask(MiscellaneousMetadataSubtaskBase):

    def process(self, tdo: URLMiscellaneousMetadataTDO):
        tdo.name = tdo.collector_metadata['title']
        tdo.description = tdo.collector_metadata['title']
