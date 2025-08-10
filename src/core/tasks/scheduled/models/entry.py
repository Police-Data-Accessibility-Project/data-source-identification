from typing import Any

from pydantic import BaseModel

from src.core.tasks.scheduled.enums import IntervalEnum
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase


class ScheduledTaskEntry(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    operator: ScheduledTaskOperatorBase
    interval: IntervalEnum
    enabled: bool
