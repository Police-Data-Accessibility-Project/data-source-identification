from pydantic import BaseModel


class BasicInput(BaseModel):
    html: str

