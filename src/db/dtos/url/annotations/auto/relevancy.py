from pydantic import BaseModel


class AutoRelevancyAnnotationInput(BaseModel):
    url_id: int
    is_relevant: bool
    confidence: float
    model_name: str