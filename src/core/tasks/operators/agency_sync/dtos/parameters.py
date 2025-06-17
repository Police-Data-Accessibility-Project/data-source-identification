from datetime import date
from typing import Optional

from pydantic import BaseModel


class AgencySyncParameters(BaseModel):
    cutoff_date: Optional[date]
    page: Optional[int]
