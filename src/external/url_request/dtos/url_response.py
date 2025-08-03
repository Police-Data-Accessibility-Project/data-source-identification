from http import HTTPStatus
from typing import Optional

from pydantic import BaseModel


class URLResponseInfo(BaseModel):
    success: bool
    status: HTTPStatus | None = None
    html: str | None = None
    content_type: str | None = None
    exception: str | None = None
