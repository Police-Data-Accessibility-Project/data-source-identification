from typing import Optional

from sqlalchemy import Select, case, Label, and_, exists
from sqlalchemy.sql.functions import count, coalesce

from src.collectors.enums import URLStatus, CollectorType
from src.core.enums import BatchStatus
from src.db.models.impl.link.batch_url import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.queries.base.builder import QueryBuilderBase
from src.db.queries.helpers import add_page_offset
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.labels import URLCountsLabels


class URLCountsCTEQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        page: int = 1,
        has_pending_urls: Optional[bool] = None,
        collector_type: Optional[CollectorType] = None,
        status: Optional[BatchStatus] = None,
        batch_id: Optional[int] = None
    ):
        super().__init__(URLCountsLabels())
        self.page = page
        self.has_pending_urls = has_pending_urls
        self.collector_type = collector_type
        self.status = status
        self.batch_id = batch_id


    def get_core_query(self):
        labels: URLCountsLabels = self.labels
        return (
            Select(
                Batch.id.label(labels.batch_id),
                coalesce(count(URL.id), 0).label(labels.total),
                self.count_case_url_status(URLStatus.PENDING, labels.pending),
                self.count_case_url_status(URLStatus.SUBMITTED, labels.submitted),
                self.count_case_url_status(URLStatus.NOT_RELEVANT, labels.not_relevant),
                self.count_case_url_status(URLStatus.ERROR, labels.error),
                self.count_case_url_status(URLStatus.DUPLICATE, labels.duplicate),
            )
            .select_from(Batch)
            .outerjoin(LinkBatchURL)
            .outerjoin(
                URL
            )
        )


    def build(self):
        query = self.get_core_query()
        query = self.apply_pending_urls_filter(query)
        query = self.apply_collector_type_filter(query)
        query = self.apply_status_filter(query)
        query = self.apply_batch_id_filter(query)
        query = query.group_by(Batch.id)
        query = add_page_offset(query, page=self.page)
        query = query.order_by(Batch.id)
        self.query = query.cte("url_counts")

    def apply_batch_id_filter(self, query: Select):
        if self.batch_id is None:
            return query
        return query.where(Batch.id == self.batch_id)

    def apply_pending_urls_filter(self, query: Select):
        if self.has_pending_urls is None:
            return query
        pending_url_subquery = (
            exists(
                Select(URL).join(LinkBatchURL).where(
                    and_(
                        LinkBatchURL.batch_id == Batch.id,
                        URL.status == URLStatus.PENDING.value
                    )
                )
            )
        ).correlate(Batch)
        if self.has_pending_urls:
            return query.where(pending_url_subquery)
        return query.where(~pending_url_subquery)

    def apply_collector_type_filter(self, query: Select):
        if self.collector_type is None:
            return query
        return query.where(Batch.strategy == self.collector_type.value)

    def apply_status_filter(self, query: Select):
        if self.status is None:
            return query
        return query.where(Batch.status == self.status.value)

    @staticmethod
    def count_case_url_status(
        url_status: URLStatus,
        label: str
    ) -> Label:
        return (
            coalesce(
                count(
                    case(
                        (URL.status == url_status.value, 1)
                    )
                )
            , 0).label(label)
        )
