from src.db.models.impl.url.suggestion.relevant.auto.pydantic.input import AutoRelevancyAnnotationInput
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase


class AutoRelevantSuggestionCommand(DBDataCreatorCommandBase):

    def __init__(
        self,
        url_id: int,
        relevant: bool = True
    ):
        super().__init__()
        self.url_id = url_id
        self.relevant = relevant

    async def run(self) -> None:
        await self.adb_client.add_auto_relevant_suggestion(
            input_=AutoRelevancyAnnotationInput(
                url_id=self.url_id,
                is_relevant=self.relevant,
                confidence=0.5,
                model_name="test_model"
            )
        )
