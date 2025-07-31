from pydantic import BaseModel

from src.db.client.async_ import AsyncDatabaseClient
from src.db.client.sync import DatabaseClient


class DBDataCreatorClientContainer(BaseModel):
    db: DatabaseClient
    adb: AsyncDatabaseClient

    class Config:
        arbitrary_types_allowed = True
