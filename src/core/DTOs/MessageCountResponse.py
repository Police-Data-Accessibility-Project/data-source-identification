from pydantic import Field

from src.core.DTOs.MessageResponse import MessageResponse


class MessageCountResponse(MessageResponse):
    count: int = Field(description="The associated count")