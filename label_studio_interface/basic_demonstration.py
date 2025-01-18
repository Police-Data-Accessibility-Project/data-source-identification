"""
This script will serve as a basic demonstration of the functionality of
Label Studio and the Python configuration developed.

The script will:
    1. Load the configuration for the Label Studio API
    2. Delete all task data from the associated project in Label Studio (if any exists)
    3. Import new task data into the project
    4. Prompt the user to access Label Studio and perform review and annotation tasks
    5. Export the annotated data from Label Studio and present it to the user

The configuration for the Label Studio API will be loaded from the dev.env file within this directory
However, the access token in the file is not valid and will need to be replaced with a valid access token

All actions will be performed on the 'Simple URL Labeler" project viewable at https://app.heartex.com/projects/58903/
"""

from LabelStudioAPIManager import LabelStudioAPIManager
from LabelStudioConfig import LabelStudioConfig

# Simple URL Labeler project URL
project_url = "https://app.heartex.com/projects/58903/"

# Load the configuration for the Label Studio API
config = LabelStudioConfig("dev.env")
if "REPLACE_WITH_YOUR_TOKEN" in config.authorization_token:
    raise ValueError("Please replace the access token in dev.env with your own access token")

# Create an API manager
api_manager = LabelStudioAPIManager(config)

print("Deleting project tasks...")
# Delete all task data from the associated project in Label Studio (if any exists)
api_manager.delete_project_tasks()

# Prompt the user to access Label Studio and confirm that the project has been cleared
print(f"Please access the project at {project_url} to confirm that the project has been cleared")

# Wait for the user to confirm that the project has been cleared
input("Press Enter once confirmed...")
print("Continuing...")

# Import new task data into the project
# Two tasks will be imported: one which has not been annotated and one which has been pre-annotated
# These tasks are provided in their final data form,
# but will need to be converted into this form in the eventual pipeline
data = [
    {
        "data": {
            "url": "https://test_data.gov/test/test-services/annual-test/"
        }
    },
    {
        "data": {
            "url": "www.example.com"
        },
        "annotations": [
            {
                "result": [
                    {
                        "type": "taxonomy",
                        "value": {
                            "taxonomy": [
                                [
                                    "Police Public Interactions"
                                ],
                                [
                                    "Police Public Interactions",
                                    "Accident Reports"
                                ],
                                [
                                    "Police Public Interactions",
                                    "Arrest Records"
                                ],
                                [
                                    "Agency Published Resources"
                                ],
                                [
                                    "Agency Published Resources",
                                    "Crime Maps and Reports"
                                ],
                                [
                                    "Non-Criminal Justice"
                                ]
                            ]
                        },
                        "origin": "manual",
                        "to_name": "url_text",
                        "from_name": "category"
                    },
                    {
                        "type": "choices",
                        "value": {
                            "choices": [
                                "Y"
                            ]
                        },
                        "origin": "manual",
                        "to_name": "is_single_record",
                        "from_name": "single_record_checkbox"
                    }
                ]
            }
        ]
    }
]
api_manager.export_tasks_into_project(data)

# Prompt the user to access Label Studio and perform review and annotation tasks
print(f"Please access the project at {project_url} to perform review and annotation tasks")

# Wait for the user to complete the tasks
input("Press Enter when complete...")
print("Continuing...")

# Import the annotated data from Label Studio and present it to the user
response = api_manager.import_tasks_from_project(all_tasks=True)
print("Presenting annotated data (showing only first results)...")
results = response.json()
for result in results:
    print(f"Task URL: {result['data']['url']}")
    if len(result['annotations']) == 0:
        print("No annotations")
    else:
        print(f"Annotations: {result['annotations'][0]['result']}")
        print("\n")
