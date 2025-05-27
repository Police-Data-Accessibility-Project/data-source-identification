from collector_manager.ExampleCollector import ExampleCollector
from collector_manager.enums import CollectorType
from src.source_collectors.auto_googler.AutoGooglerCollector import AutoGooglerCollector
from src.source_collectors.ckan import CKANCollector
from src.source_collectors.common_crawler import CommonCrawlerCollector
from src.source_collectors.muckrock.classes import MuckrockSimpleSearchCollector, \
    MuckrockCountyLevelSearchCollector, MuckrockAllFOIARequestsCollector

COLLECTOR_MAPPING = {
    CollectorType.EXAMPLE: ExampleCollector,
    CollectorType.AUTO_GOOGLER: AutoGooglerCollector,
    CollectorType.COMMON_CRAWLER: CommonCrawlerCollector,
    CollectorType.MUCKROCK_SIMPLE_SEARCH: MuckrockSimpleSearchCollector,
    CollectorType.MUCKROCK_COUNTY_SEARCH: MuckrockCountyLevelSearchCollector,
    CollectorType.MUCKROCK_ALL_SEARCH: MuckrockAllFOIARequestsCollector,
    CollectorType.CKAN: CKANCollector
}
