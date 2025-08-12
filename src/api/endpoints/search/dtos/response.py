from typing import Optional

from pydantic import BaseModel


class SearchURLResponse(BaseModel):
    found: bool
    url_id: int | None = None