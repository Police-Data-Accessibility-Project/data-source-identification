from typing import final

from typing_extensions import override

from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType


@final
class URLRootURLTaskOperator(URLTaskOperatorBase):

    def __init__(self, adb_client: AsyncDatabaseClient):
        super().__init__(adb_client)

    @override
    def meets_task_prerequisites(self) -> bool:
        raise NotImplementedError

    @property
    @override
    def task_type(self) -> TaskType:
        return TaskType.ROOT_URL

    @override
    async def inner_task_logic(self) -> None:
        raise NotImplementedError