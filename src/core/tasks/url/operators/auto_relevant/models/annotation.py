from pydantic import BaseModel


class RelevanceAnnotationInfo(BaseModel):
    is_relevant: bool
    confidence: float
    model_name: str