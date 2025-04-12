from collector_manager.enums import CollectorType

ASYNC_COLLECTORS = [
    CollectorType.AUTO_GOOGLER,
    CollectorType.EXAMPLE
]

SYNC_COLLECTORS = [
    CollectorType.MUCKROCK_SIMPLE_SEARCH,
    CollectorType.MUCKROCK_COUNTY_SEARCH,
    CollectorType.MUCKROCK_ALL_SEARCH,
    CollectorType.CKAN,
    CollectorType.COMMON_CRAWLER,
]