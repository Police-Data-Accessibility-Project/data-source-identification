import json
import os
import random
import string

import requests
from dotenv import load_dotenv


def generate_random_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


class LabelStudioAPIURLConstructor:
    """
    This class is responsible for constructing the URL for the Label Studio API.
    """

    def __init__(self, project_id: str = '58475'):
        self.label_studio_api_root_url = f'https://app.heartex.com/api/projects/{project_id}'

    def get_import_url(self) -> str:
        """
        This method returns the URL for importing data into Label Studio.
        Returns: str
        """
        return f'{self.label_studio_api_root_url}/import'

    def get_project_url(self) -> str:
        """
        This method returns the URL for the project.
        Returns: str
        """
        return f'{self.label_studio_api_root_url}'

    def get_easy_export_url(self, all_tasks: bool) -> str:
        """
        This method returns the URL for the easy export.
        Returns: str
        """
        url = f'{self.label_studio_api_root_url}/export?exportType=JSON'
        if all_tasks:
            url += '&download_all_tasks=true'
        return url

class LabelStudioAPIManager:

    def __init__(
            self,
            project_id: str = '58475',
            authorization_token: str = 'abc123'
    ):
        self.api_url_constructor = LabelStudioAPIURLConstructor(
            project_id=project_id
        )
        self.authorization_token = f'Token {authorization_token}'

    def import_data(self, data: list[dict]) -> requests.Response:
        """
        This method imports task input data into Label Studio.
        Args:
            data: dict - The data to import into Label Studio.
                This should be a list of dictionaries, each containing
                the same keys, representing data for the task
        Returns: requests.Response
        """
        import_url = self.api_url_constructor.get_import_url()
        response = requests.post(
            url=import_url,
            data=json.dumps(data),
            # TODO: Consider extracting header construction
            headers={
                'Content-Type': 'application/json',
                'Authorization': self.authorization_token
            }
        )
        return response

    def get_project_info(self) -> requests.Response:
        """
        This method retrieves information about the project.
        Returns: requests.Response
        """
        project_url = self.api_url_constructor.get_project_url()
        response = requests.get(
            url=project_url,
            headers={
                'Authorization': self.authorization_token
            }
        )
        return response

    def get_project_tasks(self, all_tasks: bool = False) -> requests.Response:
        """
        This method exports the data from the project.
        Args:
            all_tasks: bool - Whether to export all tasks or just the annotated tasks.
            output_filename: str - The filename to save the exported data to.
        Returns: requests.Response
        """
        export_url = self.api_url_constructor.get_easy_export_url(all_tasks=all_tasks)
        response = requests.get(
            url=export_url,
            headers={
                'Authorization': self.authorization_token
            }
        )
        return response

    def ping_project(self) -> bool:
        """
        This method pings the project, returning True if the project is accessible.
        Returns: bool
        """
        project_url = self.api_url_constructor.get_project_url()
        response = requests.get(
            url=project_url,
            headers={
                'Authorization': self.authorization_token
            }
        )
        return response.status_code == 200


if __name__ == "__main__":
    load_dotenv()
    # Pull authorization token from env
    authorization_token = os.getenv('LABEL_STUDIO_API_KEY')

    # Example usage
    api_manager = LabelStudioAPIManager(
        project_id='58475',
        authorization_token=authorization_token
    )
    project_accessible = api_manager.ping_project()
    if project_accessible:
        print("Project is accessible")

    # Test import
    # data = [{"url": f"https://example.com/{generate_random_word(10)}"} for _ in range(10)]
    #
    # response = api_manager.import_data(data)
    # print(response.status_code)
    # print(response.json())

    # Test export
    response = api_manager.get_project_tasks()
    print(response.status_code)
    print(response.json())

