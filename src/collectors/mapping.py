from src.collectors.enums import CollectorType
from src.collectors.impl.auto_googler.collector import AutoGooglerCollector
from src.collectors.impl.ckan.collector import CKANCollector
from src.collectors.impl.common_crawler.collector import CommonCrawlerCollector
from src.collectors.impl.example.core import ExampleCollector
from src.collectors.impl.muckrock.collectors.all_foia.core import MuckrockAllFOIARequestsCollector
from src.collectors.impl.muckrock.collectors.county.core import MuckrockCountyLevelSearchCollector
from src.collectors.impl.muckrock.collectors.simple.core import MuckrockSimpleSearchCollector

COLLECTOR_MAPPING = {
    CollectorType.EXAMPLE: ExampleCollector,
    CollectorType.AUTO_GOOGLER: AutoGooglerCollector,
    CollectorType.COMMON_CRAWLER: CommonCrawlerCollector,
    CollectorType.MUCKROCK_SIMPLE_SEARCH: MuckrockSimpleSearchCollector,
    CollectorType.MUCKROCK_COUNTY_SEARCH: MuckrockCountyLevelSearchCollector,
    CollectorType.MUCKROCK_ALL_SEARCH: MuckrockAllFOIARequestsCollector,
    CollectorType.CKAN: CKANCollector
}
