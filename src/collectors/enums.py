from enum import Enum

class CollectorType(Enum):
    EXAMPLE = "example"
    AUTO_GOOGLER = "auto_googler"
    COMMON_CRAWLER = "common_crawler"
    MUCKROCK_SIMPLE_SEARCH = "muckrock_simple_search"
    MUCKROCK_COUNTY_SEARCH = "muckrock_county_search"
    MUCKROCK_ALL_SEARCH = "muckrock_all_search"
    CKAN = "ckan"
    MANUAL = "manual"

class URLStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    VALIDATED = "validated"
    ERROR = "error"
    DUPLICATE = "duplicate"
    NOT_RELEVANT = "not relevant"
    NOT_FOUND = "404 not found"
    INDIVIDUAL_RECORD = "individual record"
