from src.core.DTOs.task_data_objects.URLMiscellaneousMetadataTDO import URLMiscellaneousMetadataTDO
from src.core.classes.subtasks.MiscellaneousMetadata.MiscellaneousMetadataSubtaskBase import \
    MiscellaneousMetadataSubtaskBase


class CKANMiscMetadataSubtask(MiscellaneousMetadataSubtaskBase):

    def process(self, tdo: URLMiscellaneousMetadataTDO):
        tdo.name = tdo.collector_metadata['submitted_name']
        tdo.description = tdo.collector_metadata['description']
        tdo.record_formats = tdo.collector_metadata['record_format']
        tdo.data_portal_type = tdo.collector_metadata['data_portal_type']
        tdo.supplying_entity = tdo.collector_metadata['supplying_entity']
