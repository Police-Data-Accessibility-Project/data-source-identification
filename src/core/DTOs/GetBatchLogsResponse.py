from pydantic import BaseModel

from src.db.DTOs.LogInfo import LogOutputInfo


class GetBatchLogsResponse(BaseModel):
    logs: list[LogOutputInfo]