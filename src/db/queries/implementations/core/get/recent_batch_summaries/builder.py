from typing import Optional

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.batch.dtos.get.summaries.counts import BatchSummaryURLCounts
from src.api.endpoints.batch.dtos.get.summaries.summary import BatchSummary
from src.collectors.enums import CollectorType
from src.core.enums import BatchStatus
from src.db.models.instantiations.batch.sqlalchemy import Batch
from src.db.queries.base.builder import QueryBuilderBase
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.builder import URLCountsCTEQueryBuilder
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.labels import URLCountsLabels


class GetRecentBatchSummariesQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        page: int = 1,
        has_pending_urls: Optional[bool] = None,
        collector_type: Optional[CollectorType] = None,
        status: Optional[BatchStatus] = None,
        batch_id: Optional[int] = None,
    ):
        super().__init__()
        self.url_counts_cte = URLCountsCTEQueryBuilder(
            page=page,
            has_pending_urls=has_pending_urls,
            collector_type=collector_type,
            status=status,
            batch_id=batch_id,
        )

    async def run(self, session: AsyncSession) -> list[BatchSummary]:
        self.url_counts_cte.build()
        builder = self.url_counts_cte
        count_labels: URLCountsLabels = builder.labels

        query = Select(
            *builder.get_all(),
            Batch.strategy,
            Batch.status,
            Batch.parameters,
            Batch.user_id,
            Batch.compute_time,
            Batch.date_generated,
        ).join(
            builder.query,
            builder.get(count_labels.batch_id) == Batch.id,
        )
        raw_results = await session.execute(query)

        summaries: list[BatchSummary] = []
        for row in raw_results.mappings().all():
            summaries.append(
                BatchSummary(
                    id=row.id,
                    strategy=row.strategy,
                    status=row.status,
                    parameters=row.parameters,
                    user_id=row.user_id,
                    compute_time=row.compute_time,
                    date_generated=row.date_generated,
                    url_counts=BatchSummaryURLCounts(
                        total=row[count_labels.total],
                        duplicate=row[count_labels.duplicate],
                        not_relevant=row[count_labels.not_relevant],
                        submitted=row[count_labels.submitted],
                        errored=row[count_labels.error],
                        pending=row[count_labels.pending],
                    ),
                )
            )

        return summaries
