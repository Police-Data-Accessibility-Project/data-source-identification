from typing import Optional

from pydantic import BaseModel

from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.url.enums import TaskOperatorOutcome


class URLTaskOperatorRunInfo(TaskOperatorRunInfo):
    linked_url_ids: list[int]
