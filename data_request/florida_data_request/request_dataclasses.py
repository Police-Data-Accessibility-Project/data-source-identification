from dataclasses import dataclass

from data_request.florida_data_request.request_enums import QueryType


@dataclass
class QueryInfo:
    query_id: int
    query_text: str

@dataclass
class SearchResult:
    result_id: int
    title: str
    url: str
    snippet: str

@dataclass
class QueryAndSearchResults:
    query_id: int
    query_text: str
    search_results: list[SearchResult]


@dataclass
class MostRelevantResult:
    result_id: int
    rationale: str

