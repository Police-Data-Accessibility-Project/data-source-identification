import datetime

from pydantic import BaseModel


class GetMetricsURLsAggregatedResponseDTO(BaseModel):
    count_urls_total: int
    count_urls_pending: int
    count_urls_submitted: int
    count_urls_rejected: int
    count_urls_validated: int
    count_urls_errors: int
    oldest_pending_url_created_at: datetime.datetime
    oldest_pending_url_id: int