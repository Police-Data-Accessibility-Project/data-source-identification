"""
This module contains the functionality for
running type and docstyle checking on the repository
"""

import re
import subprocess
import os
import sys

# The below code sets the working directory to be the root of the entire repository
# This is done to solve otherwise quite annoying import issues.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from util.miscellaneous_functions import get_project_root, print_header

MYPY_COMMAND = 'mypy --ignore-missing-imports --disallow-untyped-defs '

MYPY_ERROR_KEYWORD = "error"
PYDOCSTYLE_ERROR_KEYWORD = "missing"


def find_pydocstyle_config() -> str:
    """
    Find the .pydocstyle config file, located at the root of the repository
    and return the --config argument along with the path
    """
    root_path = get_project_root()
    config_file = os.path.join(root_path, ".pydocstyle")
    if os.path.exists(config_file):
        return f"--config={config_file} "


PYDOCSTYLE_COMMAND = 'pydocstyle ' + find_pydocstyle_config()


def run_command(command: str) -> str:
    """Executes a shell command and returns the standard output."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Called Process Error is expected in execution if type hinting or docstring errors exist
        return e.stdout

def find_modified_python_files() -> list[str]:
    """Find modified Python files between the base and head branches with enhanced debugging."""
    base_ref = os.getenv('GITHUB_BASE_REF')
    head_ref = os.getenv('GITHUB_HEAD_REF')
    head_repo_path = os.getenv('HEAD_REPO_PATH')

    if not base_ref or not head_ref:
        print("Required environment variables are not set.")
        return []

    # Check if head repo is a fork
    if head_repo_path:
        head_ref = f"{head_repo_path}/{head_ref}"

    command_to_run = f"git diff --name-only origin/{base_ref} $(git merge-base origin/{base_ref} {head_ref}) | grep '\.py$'"

    print(f"Running command: {command_to_run}")
    modified_files_raw = run_command(command_to_run)

    if modified_files_raw == "":
        print("No output from command, potentially due to an error or no files changed.")
        return []

    modified_files = modified_files_raw.strip().split()
    print(f"Modified files: {modified_files}")
    return modified_files


def run_and_get_errored_outputs(files_to_check: list[str], command: str) -> list[str]:
    """Run a given command on specified files and return the outputs that include errors."""
    errored_outputs = []
    for file_to_check in files_to_check:
        # Ensure proper spacing and quoting of filenames in case they contain spaces or special characters
        full_command = f"{command} '{file_to_check}'"
        print(f"Running command: {full_command}")  # Logging the command to be executed for easier debugging
        output = run_command(full_command)
        if has_errors(output):
            errored_outputs.append(output)
        else:
            print(f"No errors found in {file_to_check}")  # Optional: Log files with no errors for clarity
    return errored_outputs

def has_errors(output: str) -> bool:
    """Checks for specific keywords to indicate the presence of errors"""
    error_indicators = [MYPY_ERROR_KEYWORD, PYDOCSTYLE_ERROR_KEYWORD]
    return any(indicator in output.lower() for indicator in error_indicators)


def check_files(files_to_check: list[str]) -> tuple[list[str], list[str]]:
    """
    Checks the specified files to see if they contain mypy or pydocstyle errors.
    Returns those errors if they exist.
    """
    if not files_to_check:
        print("No Python files were modified.")
        return [], []

    print(f"Checking {len(files_to_check)} files for mypy and pydocstyle errors.")
    mypy_errors = run_and_get_errored_outputs(files_to_check, MYPY_COMMAND)
    pydocstyle_errors = run_and_get_errored_outputs(files_to_check, PYDOCSTYLE_COMMAND)

    if mypy_errors:
        print(f"Mypy detected errors in {len(mypy_errors)} files.")
    if pydocstyle_errors:
        print(f"Pydocstyle detected style issues in {len(pydocstyle_errors)} files.")

    return mypy_errors, pydocstyle_errors

def announce_errors(mypy_errors: list[str], pydocstyle_errors: list[str]):
    """Announce errors if present"""
    print_header("MYPY RESULTS")
    for output in mypy_errors:
        # Because each file is individually run, the below string pattern occurs regularly.
        # The below re.sub action is designed to remove it.
        output = re.sub(r'\nFound \d+ errors* in \d+ files* \(checked 1 source file\)', '', output)
        print(output)
    print_header("PYDOCSTYLE RESULTS")
    for output in pydocstyle_errors:
        print(output)


if __name__ == "__main__":
    files = find_modified_python_files()
    mypy_errors, pydocstyle_errors = check_files(files)
    announce_errors(mypy_errors, pydocstyle_errors)
    if len(mypy_errors) > 0 or len(pydocstyle_errors) > 0:
        print("Errors detected in mypy or pydocstyle")
        exit(1)
