import os
from enum import Enum
from pathlib import Path
from typing import Type

from dotenv import load_dotenv
from pydantic import BaseModel

def get_project_root(marker_files=(".project-root",)) -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if any((parent / marker).exists() for marker in marker_files):
            return parent
    raise FileNotFoundError("No project root found (missing marker files)")

def project_path(*parts: str) -> Path:
    return get_project_root().joinpath(*parts)

def get_enum_values(enum: Type[Enum]) -> list[str]:
    return [item.value for item in enum]

def get_from_env(key: str, allow_none: bool = False):
    load_dotenv()
    val = os.getenv(key)
    if val is None and not allow_none:
        raise ValueError(f"Environment variable {key} is not set")
    return val

def load_from_environment(keys: list[str]) -> dict[str, str]:
    """
    Load selected keys from environment, returning a dictionary
    """
    original_environment = os.environ.copy()
    try:
        load_dotenv()
        return {key: os.getenv(key) for key in keys}
    finally:
        # Restore the original environment
        os.environ.clear()
        os.environ.update(original_environment)

def base_model_list_dump(model_list: list[BaseModel]) -> list[dict]:
    return [model.model_dump() for model in model_list]

def update_if_not_none(target: dict, source: dict) -> None:
    """
    Modifies:
        target
    """
    for key, value in source.items():
        if value is not None:
            target[key] = value