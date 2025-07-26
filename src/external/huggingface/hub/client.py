
from datasets import Dataset


class HuggingFaceHubClient:

    def __init__(self, token: str):
        self.token = token

    def push_dataset_to_hub(self, repo_id: str, dataset: Dataset):
        dataset.push_to_hub(repo_id=repo_id, token=self.token)
