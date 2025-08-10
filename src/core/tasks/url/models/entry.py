from pydantic import BaseModel

from src.core.tasks.url.operators.base import URLTaskOperatorBase


class URLTaskEntry(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    operator: URLTaskOperatorBase
    enabled: bool