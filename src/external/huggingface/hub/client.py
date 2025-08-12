
from datasets import Dataset
from huggingface_hub import HfApi

from src.external.huggingface.hub.constants import DATA_SOURCES_RAW_REPO_ID
from src.external.huggingface.hub.format import format_as_huggingface_dataset
from src.core.tasks.scheduled.impl.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput


class HuggingFaceHubClient:

    def __init__(self, token: str):
        self.token = token
        self.api = HfApi(token=token)

    def _push_dataset_to_hub(
        self,
        repo_id: str,
        dataset: Dataset,
        idx: int
    ) -> None:
        """
        Modifies:
            - repository on Hugging Face, identified by `repo_id`
        """
        dataset.to_parquet(f"part_{idx}.parquet")
        self.api.upload_file(
            path_or_fileobj=f"part_{idx}.parquet",
            path_in_repo=f"data/part_{idx}.parquet",
            repo_id=repo_id,
            repo_type="dataset",
        )

    def push_data_sources_raw_to_hub(
        self,
        outputs: list[GetForLoadingToHuggingFaceOutput],
        idx: int
    ) -> None:
        """
        Modifies:
            - repository on Hugging Face, identified by `DATA_SOURCES_RAW_REPO_ID`
        """
        dataset = format_as_huggingface_dataset(outputs)
        print(dataset)
        self._push_dataset_to_hub(
            repo_id=DATA_SOURCES_RAW_REPO_ID,
            dataset=dataset,
            idx=idx
        )