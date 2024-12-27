from typing import Optional

from pydantic import BaseModel

from collector_manager.enums import URLOutcome


class URLInfo(BaseModel):
    id: Optional[int] = None
    batch_id: Optional[int] = None
    url: str
    url_metadata: Optional[dict] = None
    outcome: URLOutcome = URLOutcome.PENDING
