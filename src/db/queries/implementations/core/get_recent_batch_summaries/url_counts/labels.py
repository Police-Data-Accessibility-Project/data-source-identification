from dataclasses import dataclass

from src.db.queries.base.labels import LabelsBase


@dataclass(frozen=True)
class URLCountsLabels(LabelsBase):
    batch_id: str = "id"
    total: str = "count_total"
    pending: str = "count_pending"
    submitted: str = "count_submitted"
    not_relevant: str = "count_not_relevant"
    error: str = "count_error"
    duplicate: str = "count_duplicate"


