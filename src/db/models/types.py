from src.core.enums import BatchStatus, RecordType
from src.db.enums import PGEnum
from src.util.helper_functions import get_enum_values

batch_status_enum = PGEnum('ready to label', 'error', 'in-process', 'aborted', name='batch_status')
record_type_values = get_enum_values(RecordType)
