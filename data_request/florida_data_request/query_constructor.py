"""
Constructs queries for data requests
"""
from dataclasses import dataclass


@dataclass
class QueryInfo:
    agency_id: str
    agency_name: str
    state: str
    zip: str


def build_misconduct_query(query_info: QueryInfo) -> str:
    return f"{query_info.agency_name} {query_info.state} {query_info.zip} Misconduct Reports"
