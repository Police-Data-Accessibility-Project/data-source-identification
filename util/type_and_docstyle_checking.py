"""
This module contains the functionality for
running type and docstyle checking on the repository
"""

import re
import subprocess
import os

from util.miscellaneous_functions import get_project_root

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
    """Utility function to run a shell command and capture the output."""
    command_result = subprocess.run(command, text=True, shell=True, capture_output=True)
    print_errors(command_result)
    return command_result.stdout.strip()


def print_errors(command_result: subprocess.CompletedProcess):
    """Prints the error message if any."""
    if command_result.stderr:
        print("Error:", command_result.stderr)


def find_modified_python_files() -> list[str]:
    """Find modified Python files between the base and head branches."""
    base_ref = os.getenv('GITHUB_BASE_REF')
    head_ref = os.getenv('GITHUB_HEAD_REF')

    command_to_run = f"""git diff --name-only 
        origin/{base_ref} 
        $(git merge-base origin/{base_ref} origin/{head_ref}) 
        | grep '\.py$'
    """
    modified_files_raw = run_command(command_to_run)

    modified_files = modified_files_raw.split()
    return modified_files


def run_and_get_errored_outputs(files_to_check: list[str], command: str) -> list[str]:
    """Run a given command on the specified files and return the outputs, if they include errors"""
    errored_outputs = []
    for file_to_check in files_to_check:
        output = run_command(command + ' ' + file_to_check)
        if has_errors(output):
            errored_outputs.append(output)
    return errored_outputs


def has_errors(output: str) -> bool:
    """Checks for specific keywords to indicate the presence of errors"""
    return MYPY_ERROR_KEYWORD in output.lower() or PYDOCSTYLE_ERROR_KEYWORD in output.lower()


def check_files(files_to_check: list[str]) -> tuple[list[str], list[str]]:
    """
    Checks the specified files to see if they contain mypy or pydocstyle errors
    Returns those errors if they exist
    """
    if files_to_check:
        mypy_errors = run_and_get_errored_outputs(files_to_check, MYPY_COMMAND)
        pydocstyle_errors = run_and_get_errored_outputs(files_to_check, PYDOCSTYLE_COMMAND)
        return mypy_errors, pydocstyle_errors
    else:
        print("No Python files were modified.")
        return [], []


def announce_errors(mypy_errors: list[str], pydocstyle_errors: list[str]):
    """Announce errors if present"""
    print("\nMYPY RESULTS:\n")
    for output in mypy_errors:
        output = re.sub(r'\nFound \d+ errors* in 1 file \(checked 1 source file\)', '', output)
        print(output)
    print("\nPYDOCSTYLE RESULTS:\n")
    for output in pydocstyle_errors:
        print(output)


if __name__ == "__main__":
    files = find_modified_python_files()
    mypy_errors, pydocstyle_errors = check_files(files)
    announce_errors(mypy_errors, pydocstyle_errors)
    if len(mypy_errors) > 0 or len(pydocstyle_errors) > 0:
        print("Errors detected in mypy or pydocstyle")
        exit(1)
