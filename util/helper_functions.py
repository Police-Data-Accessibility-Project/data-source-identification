import os
from enum import Enum
from typing import Type

from dotenv import load_dotenv
from pydantic import BaseModel


def get_enum_values(enum: Type[Enum]):
    return [item.value for item in enum]

def get_from_env(key: str):
    load_dotenv()
    val = os.getenv(key)
    if val is None:
        raise ValueError(f"Environment variable {key} is not set")
    return val

def base_model_list_dump(model_list: list[BaseModel]) -> list[dict]:
    return [model.model_dump() for model in model_list]

def update_if_not_none(target: dict, source: dict):
    for key, value in source.items():
        if value is not None:
            target[key] = value