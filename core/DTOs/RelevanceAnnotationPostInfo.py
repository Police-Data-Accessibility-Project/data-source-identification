from pydantic import BaseModel

from core.enums import SuggestedStatus


class RelevanceAnnotationPostInfo(BaseModel):
    suggested_status: SuggestedStatus