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
        """
        Initializes the HuggingFace API manager.
        Args:
            access_token: the HuggingFace access token
            repo_id: the repository ID
        """
        if access_token is None or len(access_token) == 0:
            raise ValueError("Access token cannot be empty.")

        huggingface_hub.login(
            token=access_token
        )
        self.api = huggingface_hub.HfApi()
        self.repo_id = repo_id

    def upload_file(self, local_file_path: Path, repo_file_path: str):
        """
        Uploads a file to the HuggingFace dataset repository.
        Args:
            local_file_path: the local file path
            repo_file_path: the file path in the repository

        Returns: None

        """
        self.api.upload_file(
            path_or_fileobj=local_file_path,
            path_in_repo=repo_file_path,
            repo_id=self.repo_id,
            repo_type="dataset"
        )
