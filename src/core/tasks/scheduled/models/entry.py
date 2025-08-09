from typing import Any

from pydantic import BaseModel

from src.core.tasks.scheduled.enums import IntervalEnum


class ScheduledTaskEntry(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    name: str
    function: Any
    interval: IntervalEnum
    kwargs: dict[str, Any] = {}