from enum import Enum as PyEnum

from sqlalchemy import TypeDecorator
from sqlalchemy.dialects import postgresql


class URLMetadataAttributeType(PyEnum):
    RECORD_TYPE = "Record Type"
    AGENCY = "Agency"
    RELEVANT = "Relevant"


class ValidationStatus(PyEnum):
    PENDING_VALIDATION = "Pending Validation"
    VALIDATED = "Validated"


class ValidationSource(PyEnum):
    MACHINE_LEARNING = "Machine Learning"
    MANUAL = "Manual"


class URLHTMLContentType(PyEnum):
    TITLE = "Title"
    DESCRIPTION = "Description"
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    H4 = "H4"
    H5 = "H5"
    H6 = "H6"
    DIV = "Div"

class TaskType(PyEnum):
    HTML = "HTML"
    RELEVANCY = "Relevancy"
    RECORD_TYPE = "Record Type"
    AGENCY_IDENTIFICATION = "Agency Identification"
    MISC_METADATA = "Misc Metadata"
    SUBMIT_APPROVED = "Submit Approved URLs"
    DUPLICATE_DETECTION = "Duplicate Detection"
    IDLE = "Idle"
    PROBE_404 = "404 Probe"
    SYNC_AGENCIES = "Sync Agencies"
    SYNC_DATA_SOURCES = "Sync Data Sources"

class ChangeLogOperationType(PyEnum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class PGEnum(TypeDecorator):
    impl = postgresql.ENUM

    cache_ok = True

    def process_bind_param(self, value: PyEnum, dialect):
        # Convert Python Enum to its value before binding to the DB
        if isinstance(value, PyEnum):
            return value.value
        return value

