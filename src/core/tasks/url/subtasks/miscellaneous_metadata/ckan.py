from src.core.tasks.url.operators.misc_metadata.tdo import URLMiscellaneousMetadataTDO
from src.core.tasks.url.subtasks.miscellaneous_metadata.base import \
    MiscellaneousMetadataSubtaskBase


class CKANMiscMetadataSubtask(MiscellaneousMetadataSubtaskBase):

    def process(self, tdo: URLMiscellaneousMetadataTDO):
        tdo.name = tdo.collector_metadata['submitted_name']
        tdo.description = tdo.collector_metadata['description']
        tdo.record_formats = tdo.collector_metadata['record_format']
        tdo.data_portal_type = tdo.collector_metadata['data_portal_type']
        tdo.supplying_entity = tdo.collector_metadata['supplying_entity']
