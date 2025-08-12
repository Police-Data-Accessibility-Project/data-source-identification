from pydantic import BaseModel

from src.db.models.impl.log.pydantic.output import LogOutputInfo


class GetBatchLogsResponse(BaseModel):
    logs: list[LogOutputInfo]