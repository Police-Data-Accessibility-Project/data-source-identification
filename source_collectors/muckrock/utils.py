"""
utils.py

Provides useful functions for muckrock_tools.

Functions:
    - format_filename_json_to_csv()
"""

import re
import json


def format_filename_json_to_csv(json_filename: str) -> str:
    """
    Converts JSON filename format to CSV filename format.

    Args:
        json_file (str): A JSON filename string.

    Returns:
        csv_filename (str): A CSV filename string.

    """
    csv_filename = re.sub(r"_(?=[^.]*$)", "-", json_filename[:-5]) + ".csv"

    return csv_filename

def load_json_file(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def save_json_file(file_path: str, data: dict | list[dict]):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)