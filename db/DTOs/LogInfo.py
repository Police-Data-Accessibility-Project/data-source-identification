from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LogInfo(BaseModel):
    id: Optional[int] = None
    log: str
    batch_id: int
    created_at: Optional[datetime] = None

class LogOutputInfo(BaseModel):
    id: Optional[int] = None
    log: str
    created_at: Optional[datetime] = None