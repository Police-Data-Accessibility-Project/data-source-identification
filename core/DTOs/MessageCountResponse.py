from pydantic import Field

from core.DTOs.MessageResponse import MessageResponse


class MessageCountResponse(MessageResponse):
    count: int = Field(description="The associated count")