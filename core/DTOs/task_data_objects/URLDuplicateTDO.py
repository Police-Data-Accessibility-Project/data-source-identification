from typing import Optional

from pydantic import BaseModel


class URLDuplicateTDO(BaseModel):
    url_id: int
    url: str
    is_duplicate: Optional[bool] = None
