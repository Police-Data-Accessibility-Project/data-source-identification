
from datasets import Dataset

from src.external.huggingface.hub.constants import DATA_SOURCES_RAW_REPO_ID
from src.external.huggingface.hub.format import format_as_huggingface_dataset
from src.core.tasks.scheduled.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput


class HuggingFaceHubClient:

    def __init__(self, token: str):
        self.token = token

    def _push_dataset_to_hub(self, repo_id: str, dataset: Dataset):
        dataset.push_to_hub(repo_id=repo_id, token=self.token)

    def push_data_sources_raw_to_hub(self, outputs: list[GetForLoadingToHuggingFaceOutput]):
        dataset = format_as_huggingface_dataset(outputs)
        print(dataset)
        self._push_dataset_to_hub(repo_id=DATA_SOURCES_RAW_REPO_ID, dataset=dataset)