from pydantic import BaseModel


class ExampleOutputDTO(BaseModel):
    message: str
    urls: list
    parameters: dict
