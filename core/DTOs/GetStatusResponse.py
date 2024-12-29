from pydantic import BaseModel

from core.enums import BatchStatus


class GetStatusResponse(BaseModel):
    batch_status: BatchStatus