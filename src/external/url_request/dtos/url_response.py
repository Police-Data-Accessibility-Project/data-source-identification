from http import HTTPStatus
from typing import Optional

from pydantic import BaseModel


class URLResponseInfo(BaseModel):
    success: bool
    status: Optional[HTTPStatus] = None
    html: Optional[str] = None
    content_type: Optional[str] = None
    exception: Optional[str] = None
