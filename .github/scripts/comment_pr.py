"""
This module is designed to interact with GitHub's API, specifically the section responsible for handling issue
comments.

Among the functions it provides is the ability to post comments on an issue using the issue's number, a repository
token for authentication and the comment content itself. It demonstrates how to make an authenticated request to
the GitHub API and handle responses from the server, raising an exception if the request was unsuccessful.

It also includes an example of usage where it reads the output of the tools `mypy` and `pydocstyle` from text files,
and formats them into a comment that is then posted to a GitHub issue corresponding to the current Git reference of
the repository that the script is being run in. The script expects certain environment variables to be present
(GITHUB_REF and GITHUB_TOKEN) and fails if they're not set.

Functions included:

- post_comment(issue_number: str, repo_token: str, message: str): Posts a comment to a specific GitHub issue.

Exceptions raised:
- requests.HTTPError: If the request to the GitHub API fails for any reason.

"""

import os
import json
import requests


def post_comment(issue_number: str, repo_token: str, message: str) -> None:
    """
    :param issue_number: The number of the issue to which the comment will be posted.
    :param repo_token: The access token required to authorize the request to the GitHub API.
    :param message: The body of the comment to be posted.
    :return: None

    This method posts a comment to a specific GitHub issue identified by `issue_number`.
    The comment is created using the provided `message`. The `repo_token` is necessary to authorize the
    * request to the GitHub API.

    Raises:
        requests.HTTPError: If the request to the GitHub API fails for any reason.
    """
    url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/issues/{issue_number}/comments"
    headers = {"Authorization": f"token {repo_token}"}
    data = {"body": message}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()


github_ref = os.getenv("GITHUB_REF")
if github_ref is None:
    raise ValueError("Environment variable GITHUB_REF is not set.")
repo_token = os.getenv("GITHUB_TOKEN")
if repo_token is None:
    raise ValueError("Environment variable GITHUB_TOKEN is not set.")
issue_number = github_ref.split("/")[-2]


# Assume you've saved the outputs to files
mypy_result = open("mypy_output.txt").read().strip()
pydocstyle_result = open("pydocstyle_output.txt").read().strip()

comment = f"## Type Hinting and Docstring Checks\n\n### mypy\n```\n{mypy_result}\n```\n### pydocstyle\n```\n{pydocstyle_result}\n```"
post_comment(issue_number, repo_token, comment)
