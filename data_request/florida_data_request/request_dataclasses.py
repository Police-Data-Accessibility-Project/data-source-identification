from dataclasses import dataclass

from data_request.florida_data_request.request_enums import QueryType


@dataclass
class QueryInfo:
    agency_id: str
    query_text: str
    query_type: QueryType
