from pydantic import BaseModel

from db.DTOs.LogInfo import LogOutputInfo


class GetBatchLogsResponse(BaseModel):
    logs: list[LogOutputInfo]