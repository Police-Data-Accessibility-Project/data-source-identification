from pydantic import BaseModel, Field


class BasicOutput(BaseModel):
    annotation: bool
    confidence: float
    model: str