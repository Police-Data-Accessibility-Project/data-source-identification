"""
This module contains utility functions for the common_crawler package
"""
import os
from collections import namedtuple

# A named tuple for results
UrlResults = namedtuple(
    typename='UrlResults',
    field_names=['index', 'search_term', 'keyword', 'page', 'url']
)

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


def get_file_path(file_name: str, directory: str = None):
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

    return full_path

def get_unique_url_roots(urls):
    return list(set([url.split('/')[2] for url in urls]))


class URLWithParameters:
    """
    A class to handle URLs with parameters, allowing for easy addition of parameters
    """

    def __init__(self, url):
        self.url = url

    def add_parameter(self, parameter, value):
        if '?' in self.url:
            self.url += f"&{parameter}={value}"
        else:
            self.url += f"?{parameter}={value}"
        return self.url

    def __str__(self):
        return self.url
