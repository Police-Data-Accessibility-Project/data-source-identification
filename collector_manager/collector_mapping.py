from collector_manager.ExampleCollector import ExampleCollector
from collector_manager.enums import CollectorType
from source_collectors.auto_googler.AutoGooglerCollector import AutoGooglerCollector
from source_collectors.ckan.CKANCollector import CKANCollector
from source_collectors.common_crawler.CommonCrawlerCollector import CommonCrawlerCollector
from source_collectors.muckrock.classes.MuckrockCollector import MuckrockSimpleSearchCollector, \
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
