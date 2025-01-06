from pydantic import BaseModel, Field


class AutoGooglerInputDTO(BaseModel):
    urls_per_result: int = Field(
        description="Maximum number of URLs returned per result. Minimum is 1. Default is 10",
        default=10,
        ge=1,
        le=10
    )
    queries: list[str] = Field(
        description="List of queries to search for.",
        min_length=1,
        max_length=100
    )

class AutoGooglerInnerOutputDTO(BaseModel):
    title: str = Field(description="The title of the result.")
    url: str = Field(description="The URL of the result.")
    snippet: str = Field(description="The snippet of the result.")

class AutoGooglerResultDTO(BaseModel):
    query: str = Field(description="The query used for the search.")
    query_results: list[AutoGooglerInnerOutputDTO] = Field(description="List of results for each query.")

class AutoGooglerOutputDTO(BaseModel):
    results: list[AutoGooglerResultDTO]

class GoogleSearchQueryResultsInnerDTO(BaseModel):
    url: str = Field(description="The URL of the result.")
    title: str = Field(description="The title of the result.")
    snippet: str = Field(description="The snippet of the result.")
