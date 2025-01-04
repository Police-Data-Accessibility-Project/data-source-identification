from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str = Field(description="The response message")