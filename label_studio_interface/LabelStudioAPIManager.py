import copy
import json
import os
import random
import string
import sys
from typing import Annotated

import requests
from dotenv import load_dotenv
from enum import Enum

from label_studio_interface.DTOs.LabelStudioTaskExportInfo import LabelStudioTaskExportInfo

# The below code sets the working directory to be the root of the entire repository
# This is done to solve otherwise quite annoying import issues.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from label_studio_interface.LabelStudioConfig import LabelStudioConfig

"""
This script contains code which interfaces with the Label Studio API.
To view the documentation for the Label Studio API, visit https://app.heartex.com/docs/api
"""


class Role(Enum):
    """
    This class represents the roles that a user can have in an organization.
    """
    OWNER = "OW"
    ADMINISTRATOR = "AD"
    MANAGER = "MA"
    REVIEWER = "RE"
    ANNOTATOR = "AN"
    DEACTIVATED = "DI"
    NONE = "NO"

def generate_random_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


class URLConstructor:
    def __init__(self, scheme="http", domain=None):
        self.scheme = scheme
        self.domain = domain
        self.path_segments = []
        self.query_params = {}

    def add_path_segment(self, segment):
        self.path_segments.append(segment)
        return self

    def add_query_param(self, key, value):
        self.query_params[key] = value
        return self

    def build(self):
        path = "/".join(self.path_segments)
        query_string = "&".join([f"{key}={value}" for key, value in self.query_params.items()])
        url = f"{self.scheme}://{self.domain}"
        if path:
            url += f"/{path}"
        if query_string:
            url += f"?{query_string}"
        return url


class LabelStudioAPIURLConstructor:
    """
    This class is responsible for constructing the URL for the Label Studio API.
    """

    def __init__(self, project_id: str = '58475', organization_id: str = '1'):
        self.base_url_constructor = URLConstructor(
            domain='app.heartex.com',
            scheme='https'
        ).add_path_segment('api')
        self.project_id = project_id
        self.organization_id = organization_id
        # self.label_studio_api_root_url = 'https://app.heartex.com/api'
        # self.label_studio_api_root_url = f'https://app.heartex.com/api/projects/{project_id}'

    def get_import_url(self) -> str:
        """
        This method returns the URL for importing data into Label Studio.
        Returns: str
        """
        new_constructor = copy.deepcopy(self.base_url_constructor)
        return (new_constructor
                .add_path_segment('projects')
                .add_path_segment(self.project_id)
                .add_path_segment('import')
                .build()
                )

    def get_project_url(self) -> str:
        """
        This method returns the URL for the project.
        Returns: str
        """
        new_constructor = copy.deepcopy(self.base_url_constructor)
        return (new_constructor
                .add_path_segment('projects')
                .add_path_segment(self.project_id)
                .build()
                )

    def delete_project_tasks_url(self) -> str:
        """
        This method returns the URL for deleting all tasks in the project.
        Returns: str
        """
        new_constructor = copy.deepcopy(self.base_url_constructor)
        return (new_constructor
                .add_path_segment('projects')
                .add_path_segment(self.project_id)
                .add_path_segment('ground-truth-tasks')
                .build()
                )

    def get_easy_export_url(self, all_tasks: bool) -> str:
        """
        This method returns the URL for the easy export.
        Returns: str
        """
        new_constructor = copy.deepcopy(self.base_url_constructor)
        return (new_constructor
                .add_path_segment('projects')
                .add_path_segment(self.project_id)
                .add_path_segment('export')
                .add_query_param('exportType', 'JSON')
                .add_query_param('download_all_tasks', str(all_tasks).lower())
                .build()
                )

    def get_organization_membership_url(self) -> str:
        """
        This method returns the URL for organization membership
        Used for querying the members in the organization as well as updating the role of a member.
        Returns: str
        """
        new_constructor = copy.deepcopy(self.base_url_constructor)
        return (new_constructor
                .add_path_segment('organizations')
                .add_path_segment(self.organization_id)
                .add_path_segment('memberships')
                .build()
                )


class LabelStudioAPIManager:

    def __init__(
            self,
            config: LabelStudioConfig = LabelStudioConfig(),
    ):
        """
        This class is responsible for managing the API requests to Label Studio.
        Args:
            config: The user's authorization token for the Label Studio API.
        """
        self.config = config
        self.api_url_constructor = LabelStudioAPIURLConstructor(
            project_id=self.config.project_id,
            organization_id=self.config.organization_id
        )

    # region Task Import/Export
    def export_tasks_into_project(
            self,
            data: list[LabelStudioTaskExportInfo]
    ) -> Annotated[int, "The resultant Label Studio import ID"]:
        """
        This method imports task input data into Label Studio.
        Args:
            data: dict - The data to import into Label Studio.
                This should be a list of dictionaries, each containing
                the same keys, representing data for the task
        Returns: requests.Response
        """
        dict_data = []
        for task in data:
            dict_data.append(task.model_dump())
        import_url = self.api_url_constructor.get_import_url()
        response = requests.post(
            url=import_url,
            data=json.dumps(dict_data),
            # TODO: Consider extracting header construction
            headers={
                'Content-Type': 'application/json',
                'Authorization': self.config.authorization_token
            }
        )
        response.raise_for_status()
        return response.json()["import"]

    def import_tasks_from_project(self, all_tasks: bool = False) -> requests.Response:
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
                'Authorization': self.config.authorization_token
            }
        )
        response.raise_for_status()
        return response

    # endregion

    # region Project Information
    def get_project_info(self) -> requests.Response:
        """
        This method retrieves information about the project.
        Returns: requests.Response
        """
        project_url = self.api_url_constructor.get_project_url()
        response = requests.get(
            url=project_url,
            headers={
                'Authorization': self.config.authorization_token
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
                'Authorization': self.config.authorization_token
            }
        )
        return response.status_code == 200

    # endregion

    # region User Management
    def get_members_in_organization(self) -> requests.Response:
        """
        This method retrieves the members in the organization.
        https://app.heartex.com/docs/api#tag/Organizations/operation/api_organizations_memberships_list
        Returns: requests.Response
        """
        membership_url = self.api_url_constructor.get_organization_membership_url()
        response = requests.get(
            url=membership_url,
            headers={
                'Authorization': self.config.authorization_token
            }
        )
        response.raise_for_status()
        return response

    def update_member_role(self, user_id: int, role: Role) -> requests.Response:
        """
        This method updates the role of a member in the organization.
        Args:
            user_id: str - The ID of the user to update the role for.
            role: Role - The role to update the user to.
        Returns: requests.Response
        """
        membership_url = self.api_url_constructor.get_organization_membership_url()
        response = requests.patch(
            url=membership_url,
            headers={
                'Authorization': self.config.authorization_token,
                'Content-Type': 'application/json'
            },
            json={
                "user_id": user_id,
                "role": role.value
            }
        )
        return response

    def delete_project_tasks(self) -> requests.Response:
        """
        This method deletes all tasks from the project.
        Returns: requests.Response
        """
        delete_url = self.api_url_constructor.delete_project_tasks_url()
        response = requests.delete(
            url=delete_url,
            headers={
                'Authorization': self.config.authorization_token
            }
        )
        return response

    # endregion


if __name__ == "__main__":

    # Example usage
    api_manager = LabelStudioAPIManager(config=LabelStudioConfig())
    project_accessible = api_manager.ping_project()
    if project_accessible:
        print("Project is accessible")

    # Test export
    # data = [{"url": f"https://example.com/{generate_random_word(10)}"} for _ in range(10)]
    #
    # response = api_manager.import_data(data)
    # print(response.status_code)
    # print(response.json())

    # Test import
    response = api_manager.import_tasks_from_project()
    print(response.status_code)
    print(response.json())
