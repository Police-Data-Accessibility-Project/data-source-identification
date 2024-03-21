import os
from datetime import datetime
from pathlib import Path


def get_filename_friendly_timestamp() -> str:
    # Get the current datetime
    now = datetime.now()
    # Format the datetime in a filename-friendly format
    # Example: "2024-03-20_15-30-45"
    return now.strftime("%Y-%m-%d_%H-%M-%S")


def create_directories_if_not_exist(file_path: str):
    """
    Create directories if they don't exist
    Args:
        file_path:

    Returns:

    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        print(f"Creating directory: {directory}")
        os.makedirs(directory)


def get_file_path(file_name: str, directory: str = None) -> Path:
    """
    Get the full path to a file
    Args:
        file_name:
        directory:

    Returns:

    """
    # Get the current working directory
    current_directory = os.getcwd()

    # If a directory is specified, interpret it as a subdirectory of the current working directory
    if directory is not None:
        directory = os.path.join(current_directory, directory)

    # If no directory is specified, use the current working directory
    else:
        directory = current_directory

    # Construct the full path to the file
    full_path = os.path.join(directory, file_name)

    # Create directories if they don't exist
    create_directories_if_not_exist(full_path)

    return Path(full_path)
