from pydantic import BaseModel


class BasicOutput(BaseModel):
    """Corresponds to `BasicOutput` model in inference repository.

    https://github.com/Police-Data-Accessibility-Project/relevance-inference/blob/main/src/dtos/output/basic.py
    """
    annotation: bool
    confidence: float
    model: str