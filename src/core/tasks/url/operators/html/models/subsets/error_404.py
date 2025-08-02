from pydantic import BaseModel

from src.core.tasks.url.operators.html.tdo import UrlHtmlTDO


class ErrorSubsets(BaseModel):
    is_404: list[UrlHtmlTDO]
    not_404: list[UrlHtmlTDO]