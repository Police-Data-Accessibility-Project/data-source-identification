from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LogOutputInfo(BaseModel):
    id: Optional[int] = None
    log: str
    created_at: Optional[datetime] = None
