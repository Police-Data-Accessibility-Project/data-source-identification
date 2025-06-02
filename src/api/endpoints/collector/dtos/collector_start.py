from pydantic import BaseModel, Field


class CollectorStartInfo(BaseModel):
    batch_id: int = Field(
        description="The batch id of the collector"
    )
    message: str = Field(
        description="The status message"
    )
