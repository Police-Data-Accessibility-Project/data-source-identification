from pydantic import BaseModel


class IACapture(BaseModel):
    timestamp: int
    original: str
    length: int
    digest: str