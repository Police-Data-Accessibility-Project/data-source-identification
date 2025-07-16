from pydantic import BaseModel

from src.core.tasks.url.operators.auto_relevant.models.annotation import RelevanceAnnotationInfo


class URLRelevantTDO(BaseModel):
    url_id: int
    html: str
    annotation: RelevanceAnnotationInfo | None = None
    error: str | None = None

