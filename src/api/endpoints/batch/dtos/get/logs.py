from pydantic import BaseModel

from src.db.models.instantiations.log.pydantic.output import LogOutputInfo


class GetBatchLogsResponse(BaseModel):
    logs: list[LogOutputInfo]