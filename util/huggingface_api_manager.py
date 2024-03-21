from pathlib import Path

import huggingface_hub

class HuggingFaceAPIManager:
    """
    A class to manage the HuggingFace API.
    """
    def __init__(
            self,
            access_token: str,
            repo_id: str
    ):
        huggingface_hub.login(
            token=access_token
        )
        self.api = huggingface_hub.HfApi()
        self.repo_id = repo_id

    def upload_file(self, local_file_path: Path, repo_file_path: str):
        self.api.upload_file(
            path_or_fileobj=local_file_path,
            path_in_repo=repo_file_path,
            repo_id=self.repo_id,
            repo_type="dataset"
        )
