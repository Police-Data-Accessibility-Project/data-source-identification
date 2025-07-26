from datetime import date

from pydantic import BaseModel


class DataSourcesSyncParameters(BaseModel):
    cutoff_date: date | None
    page: int | None
