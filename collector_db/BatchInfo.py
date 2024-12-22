from pydantic import BaseModel


class BatchInfo(BaseModel):
    strategy: str
    status: str
    count: int = 0
    strategy_success_rate: float = None
    metadata_success_rate: float = None
    agency_match_rate: float = None
    record_type_match_rate: float = None
    record_category_match_rate: float = None
    compute_time: int = None
    parameters: dict = None