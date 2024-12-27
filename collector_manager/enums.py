from enum import Enum


class CollectorStatus(Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    ERRORED = "ERRORED"
    ABORTED = "ABORTED"

class CollectorType(Enum):
    EXAMPLE = "example_collector"
    AUTO_GOOGLER = "auto_googler"
    COMMON_CRAWLER = "common_crawler"
    MUCKROCK_SIMPLE_SEARCH = "muckrock_simple_search"
    MUCKROCK_COUNTY_SEARCH = "muckrock_county_search"
    MUCKROCK_ALL_SEARCH = "muckrock_all_search"
    CKAN = "ckan"

class URLOutcome(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    HUMAN_LABELING = "human_labeling"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"
