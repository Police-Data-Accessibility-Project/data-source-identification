from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce

from src.api.endpoints.metrics.batches.aggregated.dto import GetMetricsBatchesAggregatedResponseDTO, \
    GetMetricsBatchesAggregatedInnerResponseDTO
from src.collectors.enums import URLStatus, CollectorType
from src.core.enums import BatchStatus
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer


class GetBatchesAggregatedMetricsQueryBuilder(QueryBuilderBase):

    async def run(
        self,
        session: AsyncSession
    ) -> GetMetricsBatchesAggregatedResponseDTO:
        sc = StatementComposer

        # First, get all batches broken down by collector type and status
        def batch_column(status: BatchStatus, label):
            return sc.count_distinct(
                case(
                    (
                        Batch.status == status.value,
                        Batch.id
                    )
                ),
                label=label
            )

        batch_count_subquery = select(
            batch_column(BatchStatus.READY_TO_LABEL, label="done_count"),
            batch_column(BatchStatus.ERROR, label="error_count"),
            Batch.strategy,
        ).group_by(Batch.strategy).subquery("batch_count")

        def url_column(status: URLStatus, label):
            return sc.count_distinct(
                case(
                    (
                        URL.status == status.value,
                        URL.id
                    )
                ),
                label=label
            )

        # Next, count urls
        url_count_subquery = select(
            Batch.strategy,
            url_column(URLStatus.PENDING, label="pending_count"),
            url_column(URLStatus.ERROR, label="error_count"),
            url_column(URLStatus.VALIDATED, label="validated_count"),
            url_column(URLStatus.SUBMITTED, label="submitted_count"),
            url_column(URLStatus.NOT_RELEVANT, label="rejected_count"),

        ).join(
            LinkBatchURL,
            LinkBatchURL.url_id == URL.id
        ).outerjoin(
            Batch, Batch.id == LinkBatchURL.batch_id
        ).group_by(
            Batch.strategy
        ).subquery("url_count")

        # Combine
        query = select(
            Batch.strategy,
            batch_count_subquery.c.done_count.label("batch_done_count"),
            batch_count_subquery.c.error_count.label("batch_error_count"),
            coalesce(url_count_subquery.c.pending_count, 0).label("pending_count"),
            coalesce(url_count_subquery.c.error_count, 0).label("error_count"),
            coalesce(url_count_subquery.c.submitted_count, 0).label("submitted_count"),
            coalesce(url_count_subquery.c.rejected_count, 0).label("rejected_count"),
            coalesce(url_count_subquery.c.validated_count, 0).label("validated_count")
        ).join(
            batch_count_subquery,
            Batch.strategy == batch_count_subquery.c.strategy
        ).outerjoin(
            url_count_subquery,
            Batch.strategy == url_count_subquery.c.strategy
        )
        raw_results = await session.execute(query)
        results = raw_results.all()
        d: dict[CollectorType, GetMetricsBatchesAggregatedInnerResponseDTO] = {}
        for result in results:
            d[CollectorType(result.strategy)] = GetMetricsBatchesAggregatedInnerResponseDTO(
                count_successful_batches=result.batch_done_count,
                count_failed_batches=result.batch_error_count,
                count_urls=result.pending_count + result.submitted_count +
                           result.rejected_count + result.error_count +
                           result.validated_count,
                count_urls_pending=result.pending_count,
                count_urls_validated=result.validated_count,
                count_urls_submitted=result.submitted_count,
                count_urls_rejected=result.rejected_count,
                count_urls_errors=result.error_count
            )

        total_batch_query = await session.execute(
            select(
                sc.count_distinct(Batch.id, label="count")
            )
        )
        total_batch_count = total_batch_query.scalars().one_or_none()
        if total_batch_count is None:
            total_batch_count = 0

        return GetMetricsBatchesAggregatedResponseDTO(
            total_batches=total_batch_count,
            by_strategy=d
        )