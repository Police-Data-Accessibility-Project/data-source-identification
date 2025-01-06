from pydantic import BaseModel

from collector_db.DTOs.LogInfo import LogOutputInfo


class GetBatchLogsResponse(BaseModel):
    logs: list[LogOutputInfo]