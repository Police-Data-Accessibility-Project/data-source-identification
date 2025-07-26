from typing import Protocol

from pydantic import BaseModel


def validate_has_protocol(obj: object, protocol: type[Protocol]):
    if not isinstance(obj, protocol):
        raise TypeError(f"Class must implement {protocol} protocol.")

def validate_all_models_of_same_type(objects: list[object]):
    first_model = objects[0]
    if not all(isinstance(model, type(first_model)) for model in objects):
        raise TypeError("Models must be of the same type")