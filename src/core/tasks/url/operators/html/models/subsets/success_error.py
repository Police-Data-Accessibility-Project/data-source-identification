from pydantic import BaseModel

from src.core.tasks.url.operators.html.tdo import UrlHtmlTDO


class SuccessErrorSubset(BaseModel):
    success: list[UrlHtmlTDO]
    error: list[UrlHtmlTDO]