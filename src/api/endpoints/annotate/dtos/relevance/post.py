from pydantic import BaseModel

from src.core.enums import SuggestedStatus


class RelevanceAnnotationPostInfo(BaseModel):
    suggested_status: SuggestedStatus