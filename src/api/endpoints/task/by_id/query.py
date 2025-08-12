from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.endpoints.task.by_id.dto import TaskInfo
from src.collectors.enums import URLStatus
from src.core.enums import BatchStatus
from src.db.models.impl.url.core.pydantic.info import URLInfo
from src.db.models.impl.url.error_info.pydantic import URLErrorPydanticInfo
from src.db.enums import TaskType
from src.db.models.impl.task.core import Task
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetTaskInfoQueryBuilder(QueryBuilderBase):

    def __init__(self, task_id: int):
        super().__init__()
        self.task_id = task_id

    async def run(self, session: AsyncSession) -> TaskInfo:
        # Get Task
        result = await session.execute(
            select(Task)
            .where(Task.id == self.task_id)
            .options(
                selectinload(Task.urls)
                .selectinload(URL.batch),
                selectinload(Task.error),
                selectinload(Task.errored_urls)
            )
        )
        task = result.scalars().first()
        error = task.error[0].error if len(task.error) > 0 else None
        # Get error info if any
        # Get URLs
        urls = task.urls
        url_infos = []
        for url in urls:
            url_info = URLInfo(
                id=url.id,
                batch_id=url.batch.id,
                url=url.url,
                collector_metadata=url.collector_metadata,
                status=URLStatus(url.status),
                updated_at=url.updated_at
            )
            url_infos.append(url_info)

        errored_urls = []
        for url in task.errored_urls:
            url_error_info = URLErrorPydanticInfo(
                task_id=url.task_id,
                url_id=url.url_id,
                error=url.error,
                updated_at=url.updated_at
            )
            errored_urls.append(url_error_info)
        return TaskInfo(
            task_type=TaskType(task.task_type),
            task_status=BatchStatus(task.task_status),
            error_info=error,
            updated_at=task.updated_at,
            urls=url_infos,
            url_errors=errored_urls
        )