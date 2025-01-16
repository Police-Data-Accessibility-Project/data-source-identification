from pydantic import BaseModel


class RelevanceAnnotationPostInfo(BaseModel):
    is_relevant: bool