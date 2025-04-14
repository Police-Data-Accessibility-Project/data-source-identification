import asyncio

from collector_manager.AsyncCollectorBase import AsyncCollectorBase
from collector_manager.enums import CollectorType
from core.preprocessors.AutoGooglerPreprocessor import AutoGooglerPreprocessor
from source_collectors.auto_googler.AutoGoogler import AutoGoogler
from source_collectors.auto_googler.DTOs import AutoGooglerInputDTO, AutoGooglerInnerOutputDTO
from source_collectors.auto_googler.GoogleSearcher import GoogleSearcher
from source_collectors.auto_googler.SearchConfig import SearchConfig
from util.helper_functions import get_from_env, base_model_list_dump


class AutoGooglerCollector(AsyncCollectorBase):
    collector_type = CollectorType.AUTO_GOOGLER
    preprocessor = AutoGooglerPreprocessor

    async def run_to_completion(self) -> AutoGoogler:
        dto: AutoGooglerInputDTO = self.dto
        auto_googler = AutoGoogler(
            search_config=SearchConfig(
                urls_per_result=dto.urls_per_result,
                queries=dto.queries,
            ),
            google_searcher=GoogleSearcher(
                api_key=get_from_env("GOOGLE_API_KEY"),
                cse_id=get_from_env("GOOGLE_CSE_ID"),
            )
        )
        async for log in auto_googler.run():
            self.log(log)
        return auto_googler

    async def run_implementation(self) -> None:

        auto_googler = await self.run_to_completion()

        inner_data = []
        for query in auto_googler.search_config.queries:
            query_results: list[AutoGooglerInnerOutputDTO] = auto_googler.data[query]
            inner_data.append({
                "query": query,
                "query_results": base_model_list_dump(query_results),
            })

        self.data = {"data": inner_data}

