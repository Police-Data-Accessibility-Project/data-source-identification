import pytest

from label_studio_interface.LabelStudioConfig import LabelStudioConfig
from label_studio_interface.LabelStudioAPIManager import LabelStudioAPIManager


# Setup method
@pytest.fixture
def api_manager() -> LabelStudioAPIManager:
    config = LabelStudioConfig("../.env")
    return LabelStudioAPIManager(config)

# Helper methods
def get_member_role_and_user_id(user_id: str, org_id: str, data: dict) -> tuple[str, int]:
    for result in data['results']:
        if result['organization'] == int(org_id) and result['user']['username'] == user_id:
            return result['role'], result['user']['id']

def test_export_tasks_from_project(api_manager):
    response = api_manager.export_tasks_from_project()
    assert response.status_code == 200
    print(response.json())


def test_ping_project(api_manager):
    project_accessible = api_manager.ping_project()
    assert project_accessible
    print("Project is accessible")


def test_get_members_in_organization(api_manager):
    response = api_manager.get_members_in_organization()
    assert response.status_code == 200
    print(response.json())

def test_update_member_role(api_manager):
    # Note that for this test to work, you need to ensure there is seat available for the user in the organization
    # A seat can be made available by deactivating a seat from another user
    # (Remember to reassign the seat to the user after the test)
    from label_studio_interface.LabelStudioAPIManager import Role
    username = 'resibe6343'
    response = api_manager.get_members_in_organization()
    org_id = api_manager.config.organization_id
    role, user_id = get_member_role_and_user_id(username, org_id, response.json())
    print(role)

    # Update role to Annotator
    response = api_manager.update_member_role(user_id, Role.ANNOTATOR)
    assert response.status_code == 200
    response = api_manager.get_members_in_organization()
    role, _ = get_member_role_and_user_id(username, org_id, response.json())
    assert role == Role.ANNOTATOR.value

    # Update role to Deactivated
    response = api_manager.update_member_role(user_id, Role.DEACTIVATED)
    assert response.status_code == 200
    response = api_manager.get_members_in_organization()
    role, _ = get_member_role_and_user_id(username, org_id, response.json())
    assert role == Role.DEACTIVATED.value


    # response = api_manager.update_member_role("user_id", "role")
    # assert response.status_code == 200
    # print(response.json())