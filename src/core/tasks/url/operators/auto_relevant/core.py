from src.core.tasks.url.operators.auto_relevant.models.annotation import RelevanceAnnotationInfo
from src.core.tasks.url.operators.auto_relevant.models.tdo import URLRelevantTDO
from src.core.tasks.url.operators.auto_relevant.sort import separate_success_and_error_subsets
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.suggestion.relevant.auto.pydantic.input import AutoRelevancyAnnotationInput
from src.db.models.impl.url.error_info.pydantic import URLErrorPydanticInfo
from src.db.enums import TaskType
from src.external.huggingface.inference.client import HuggingFaceInferenceClient
from src.external.huggingface.inference.models.input import BasicInput


class URLAutoRelevantTaskOperator(URLTaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        hf_client: HuggingFaceInferenceClient
    ):
        super().__init__(adb_client)
        self.hf_client = hf_client

    @property
    def task_type(self) -> TaskType:
        return TaskType.RELEVANCY

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.has_urls_with_html_data_and_without_auto_relevant_suggestion()

    async def get_tdos(self) -> list[URLRelevantTDO]:
        return await self.adb_client.get_tdos_for_auto_relevancy()

    async def inner_task_logic(self) -> None:
        tdos = await self.get_tdos()
        url_ids = [tdo.url_id for tdo in tdos]
        await self.link_urls_to_task(url_ids=url_ids)

        await self.get_ml_classifications(tdos)
        subsets = await separate_success_and_error_subsets(tdos)

        await self.put_results_into_database(subsets.success)
        await self.update_errors_in_database(subsets.error)

    async def get_ml_classifications(self, tdos: list[URLRelevantTDO]) -> None:
        """
        Modifies:
            tdo.annotation
            tdo.error
        """
        for tdo in tdos:
            try:
                input_ = BasicInput(
                    html=tdo.html
                )
                output = await self.hf_client.get_relevancy_annotation(input_)
            except Exception as e:
                tdo.error = str(e)
                continue

            annotation_info = RelevanceAnnotationInfo(
                is_relevant=output.annotation,
                confidence=output.confidence,
                model_name=output.model
            )
            tdo.annotation = annotation_info

    async def put_results_into_database(self, tdos: list[URLRelevantTDO]) -> None:
        inputs = []
        for tdo in tdos:
            input_ = AutoRelevancyAnnotationInput(
                url_id=tdo.url_id,
                is_relevant=tdo.annotation.is_relevant,
                confidence=tdo.annotation.confidence,
                model_name=tdo.annotation.model_name
            )
            inputs.append(input_)
        await self.adb_client.add_user_relevant_suggestions(inputs)

    async def update_errors_in_database(self, tdos: list[URLRelevantTDO]) -> None:
        error_infos = []
        for tdo in tdos:
            error_info = URLErrorPydanticInfo(
                task_id=self.task_id,
                url_id=tdo.url_id,
                error=tdo.error
            )
            error_infos.append(error_info)
        await self.adb_client.add_url_error_infos(error_infos)


