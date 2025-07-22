from pydantic import BaseModel


class AnnotationBatchInfo(BaseModel):
    count_annotated: int
    total_urls: int
    count_not_annotated: int