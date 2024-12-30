from collector_manager.CollectorBase import CollectorBase
from collector_manager.enums import CollectorType
from source_collectors.auto_googler.AutoGoogler import AutoGoogler
from source_collectors.auto_googler.schemas import AutoGooglerCollectorConfigSchema, \
    AutoGooglerCollectorOuterOutputSchema
from source_collectors.auto_googler.GoogleSearcher import GoogleSearcher
from source_collectors.auto_googler.SearchConfig import SearchConfig


class AutoGooglerCollector(CollectorBase):
    config_schema = AutoGooglerCollectorConfigSchema
    output_schema = AutoGooglerCollectorOuterOutputSchema
    collector_type = CollectorType.AUTO_GOOGLER

    def run_implementation(self) -> None:
        auto_googler = AutoGoogler(
            search_config=SearchConfig(
                urls_per_result=self.config["urls_per_result"],
                queries=self.config["queries"],
            ),
            google_searcher=GoogleSearcher(
                api_key=self.config["api_key"],
                cse_id=self.config["cse_id"],
            )
        )
        for log in auto_googler.run():
            self.log(log)

        inner_data = []
        for query in auto_googler.search_config.queries:
            inner_data.append({
                    "query": query,
                    "query_results": auto_googler.data[query],
            })

        self.data = {"data": inner_data}

