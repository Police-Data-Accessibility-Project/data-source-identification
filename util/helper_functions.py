from enum import Enum
from typing import Type


def get_enum_values(enum: Type[Enum]):
    return [item.value for item in enum]