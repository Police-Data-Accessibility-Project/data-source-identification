from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.core.tasks.scheduled.impl.huggingface.queries.get.enums import RecordTypeCoarse
from src.core.tasks.scheduled.impl.huggingface.queries.get.mappings import FINE_COARSE_RECORD_TYPE_MAPPING, \
    OUTCOME_RELEVANCY_MAPPING


def convert_fine_to_coarse_record_type(
    fine_record_type: RecordType
) -> RecordTypeCoarse:
    return FINE_COARSE_RECORD_TYPE_MAPPING[fine_record_type]

def convert_url_status_to_relevant(
    url_status: URLStatus
) -> bool:
    return OUTCOME_RELEVANCY_MAPPING[url_status]