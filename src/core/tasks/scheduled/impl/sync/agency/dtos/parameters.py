from datetime import date
from typing import Optional

from pydantic import BaseModel


class AgencySyncParameters(BaseModel):
    cutoff_date: date | None
    page: int | None
