from collector_manager.ExampleCollector import ExampleCollector
from collector_manager.enums import CollectorType
from source_collectors.auto_googler.AutoGooglerCollector import AutoGooglerCollector
from source_collectors.common_crawler.CommonCrawlerCollector import CommonCrawlerCollector

COLLECTOR_MAPPING = {
    CollectorType.EXAMPLE: ExampleCollector,
    CollectorType.AUTO_GOOGLER: AutoGooglerCollector,
    CollectorType.COMMON_CRAWLER: CommonCrawlerCollector
}
