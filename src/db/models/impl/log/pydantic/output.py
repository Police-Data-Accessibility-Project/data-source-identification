from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LogOutputInfo(BaseModel):
    id: int | None = None
    log: str
    created_at: datetime | None = None
