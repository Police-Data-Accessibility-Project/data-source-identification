from pydantic import BaseModel

from core.DTOs.CollectorStatusInfo import CollectorStatusInfo


class CollectorStatusResponse(BaseModel):
    active_collectors: list[CollectorStatusInfo]