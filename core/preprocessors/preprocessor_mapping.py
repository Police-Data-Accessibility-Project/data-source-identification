from collector_manager.enums import CollectorType
from core.preprocessors.AutoGooglerPreprocessor import AutoGooglerPreprocessor
from core.preprocessors.CommonCrawlerPreprocessor import CommonCrawlerPreprocessor
from core.preprocessors.ExamplePreprocessor import ExamplePreprocessor
from core.preprocessors.MuckrockPreprocessor import MuckrockPreprocessor

PREPROCESSOR_MAPPING = {
    CollectorType.AUTO_GOOGLER: AutoGooglerPreprocessor,
    CollectorType.EXAMPLE: ExamplePreprocessor,
    CollectorType.COMMON_CRAWLER: CommonCrawlerPreprocessor,
    CollectorType.MUCKROCK_SIMPLE_SEARCH: MuckrockPreprocessor,
    CollectorType.MUCKROCK_COUNTY_SEARCH: MuckrockPreprocessor,
    CollectorType.MUCKROCK_ALL_SEARCH: MuckrockPreprocessor
}
