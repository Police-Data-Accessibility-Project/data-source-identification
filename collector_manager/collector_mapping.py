from collector_manager.ExampleCollector import ExampleCollector
from collector_manager.enums import CollectorType
from source_collectors.auto_googler.AutoGooglerCollector import AutoGooglerCollector

# TODO: Look into a way to combine this with Preprocessors, perhaps through an enum shared by both
  # while maintaining separate mappings
COLLECTOR_MAPPING = {
    CollectorType.EXAMPLE: ExampleCollector,
    CollectorType.AUTO_GOOGLER: AutoGooglerCollector
}
