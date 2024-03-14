This directory handles interfacing with 
[Label Studio](https://labelstud.io/), a data labeling tool. It handles:
- Converting data from the format used by the rest of the pipeline to the format
  used by Label Studio
- Uploading data to Label Studio
- Downloading labeled data from Label Studio
- Updating member roles in Label Studio

# Environment Variables
For proper functioning of application, the following environment variables must be set in an `.env` file in the root directory:

- LABEL_STUDIO_ACCESS_TOKEN: The access token for the Label Studio API. This can be
  obtained by logging into Label Studio and navigating to the [user account section](https://app.heartex.com/user/account), where the access token can be copied.
- LABEL_STUDIO_PROJECT_ID: The project ID for the Label Studio API. This can be
  obtained by logging into Label Studio and navigating to the relevant project, where the project id will be in the URL.
- LABEL_STUDIO_ORGANIZATION_ID: The organization ID for the Label Studio API. This can
  be obtained by logging into Label Studio and navigating to the [Organization section](https://app.heartex.com/organization?page=1), where the organization ID can be copied.

# To run basic demonstration
1. Set the environment variables as described above
2. Install the required python libraries by running the following command (from the working directory):
```bash
pip install -r requirements.txt
```
2. Run the following command (from the label_studio_interface_directory):
```bash
python basic_demonstration.py
```