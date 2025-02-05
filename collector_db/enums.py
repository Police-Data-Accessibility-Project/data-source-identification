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
    LABEL_STUDIO = "Label Studio"
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

class PGEnum(TypeDecorator):
    impl = postgresql.ENUM

    def process_bind_param(self, value: PyEnum, dialect):
        # Convert Python Enum to its value before binding to the DB
        if isinstance(value, PyEnum):
            return value.value
        return value
