import os

from dotenv import load_dotenv


class LabelStudioConfig:
    """
    This class is responsible for loading the configuration for the Label Studio API.
    """
    def __init__(self, dotenv_file=".env"):
        """

        Args:
            dotenv_file: the path to the .env file which contains the configuration for the Label Studio API
        """
        load_dotenv(dotenv_file)
        # Note that if the environment variables are not set, the default values, given below, are used
        self._project_id = os.getenv('LABEL_STUDIO_PROJECT_ID', '58475')
        self._organization_id = os.getenv('LABEL_STUDIO_ORGANIZATION_ID', '1')
        self._authorization_token = f'Token {os.getenv("LABEL_STUDIO_ACCESS_TOKEN", "abc123")}'

    @property
    def project_id(self):
        return self._project_id

    @property
    def authorization_token(self):
        return self._authorization_token

    @property
    def organization_id(self):
        return self._organization_id
