from pydantic import BaseModel

from src.db.dtos.log_info import LogOutputInfo


class GetBatchLogsResponse(BaseModel):
    logs: list[LogOutputInfo]