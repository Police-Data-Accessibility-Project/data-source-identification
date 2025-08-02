from typing import Optional

from pydantic import BaseModel


class RootURLCacheResponseInfo(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    text: Optional[str] = None
    exception: Optional[Exception] = None
