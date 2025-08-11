
from src.collectors.impl.base import AsyncCollectorBase
from src.collectors.enums import CollectorType
from src.core.env_var_manager import EnvVarManager
from src.core.preprocessors.autogoogler import AutoGooglerPreprocessor
from src.collectors.impl.auto_googler.auto_googler import AutoGoogler
from src.collectors.impl.auto_googler.dtos.output import AutoGooglerInnerOutputDTO
from src.collectors.impl.auto_googler.dtos.input import AutoGooglerInputDTO
from src.collectors.impl.auto_googler.searcher import GoogleSearcher
from src.collectors.impl.auto_googler.dtos.config import SearchConfig
from src.util.helper_functions import base_model_list_dump


class AutoGooglerCollector(AsyncCollectorBase):
    collector_type = CollectorType.AUTO_GOOGLER
    preprocessor = AutoGooglerPreprocessor

    async def run_to_completion(self) -> AutoGoogler:
        dto: AutoGooglerInputDTO = self.dto
        env_var_manager = EnvVarManager.get()
        auto_googler = AutoGoogler(
            search_config=SearchConfig(
                urls_per_result=dto.urls_per_result,
                queries=dto.queries,
            ),
            google_searcher=GoogleSearcher(
                api_key=env_var_manager.google_api_key,
                cse_id=env_var_manager.google_cse_id,
            )
        )
        async for log in auto_googler.run():
            await self.log(log)
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

