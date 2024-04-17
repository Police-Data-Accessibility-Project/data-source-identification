import subprocess
import os

import pytest

MYPY_COMMAND = 'mypy --ignore-missing-imports --disallow-untyped-defs '
PYDOCSTYLE_COMMAND = 'pydocstyle '

ERROR_KEYWORD = "error"

def find_pydocstyle_config():



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


def get_file_string(modified_files: list[str]) -> str:
    return '\'' + "\' \'".join(modified_files) + '\''


def run_and_get_errored_outputs(files_to_check: list[str], command: str):
    errored_outputs = []
    for file_to_check in files_to_check:
        output = run_command(command + ' ' + file_to_check)
        if has_errors(output):
            errored_outputs.append(output)
    return errored_outputs

def has_errors(output):
    return ERROR_KEYWORD in output.lower()


def check_files(files_to_check: list[str]):
    if files_to_check:

        mypy_outputs = run_and_get_errored_outputs(files_to_check, MYPY_COMMAND)
        print("Mypy Results:\n")
        for output in mypy_outputs:
            output = output.replace('\nFound 1 error in 1 file (checked 1 source file)', '')
            print(output)
        pydocstyle_outputs = run_and_get_errored_outputs(files_to_check, PYDOCSTYLE_COMMAND)
        print("Pydocstyle Results:\n")
        for output in pydocstyle_outputs:
            print(output)

        # if has_errors(mypy_result) or has_errors(pydocstyle_result):
        #     print("Errors detected in mypy or pydocstyle")
        #     exit(1)
    else:
        print("No Python files were modified.")


if __name__ == "__main__":
    files = find_modified_python_files()
    check_files(files)
