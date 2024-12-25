from collector_manager.enums import CollectorType
from core.preprocessors.AutoGooglerPreprocessor import AutoGooglerPreprocessor
from core.preprocessors.CommonCrawlerPreprocessor import CommonCrawlerPreprocessor
from core.preprocessors.ExamplePreprocessor import ExamplePreprocessor

PREPROCESSOR_MAPPING = {
    CollectorType.AUTO_GOOGLER: AutoGooglerPreprocessor,
    CollectorType.EXAMPLE: ExamplePreprocessor,
    CollectorType.COMMON_CRAWLER: CommonCrawlerPreprocessor
}
