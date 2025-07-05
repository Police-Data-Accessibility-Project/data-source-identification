from pydantic import BaseModel

from src.db.dtos.log import LogOutputInfo


class GetBatchLogsResponse(BaseModel):
    logs: list[LogOutputInfo]