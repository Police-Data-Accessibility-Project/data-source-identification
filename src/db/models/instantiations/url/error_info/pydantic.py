import datetime
from typing import Optional

from pydantic import BaseModel

from src.db.models.instantiations.url.error_info.sqlalchemy import URLErrorInfo
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLErrorPydanticInfo(BulkInsertableModel):
    task_id: int
    url_id: int
    error: str
    updated_at: datetime.datetime = None

    @classmethod
    def sa_model(cls) -> type[Base]:
        return URLErrorInfo