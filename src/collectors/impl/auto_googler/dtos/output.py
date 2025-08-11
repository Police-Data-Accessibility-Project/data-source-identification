from pydantic import BaseModel, Field


class AutoGooglerInnerOutputDTO(BaseModel):
    title: str = Field(description="The title of the result.")
    url: str = Field(description="The URL of the result.")
    snippet: str = Field(description="The snippet of the result.")


class AutoGooglerResultDTO(BaseModel):
    query: str = Field(description="The query used for the search.")
    query_results: list[AutoGooglerInnerOutputDTO] = Field(description="List of results for each query.")


class AutoGooglerOutputDTO(BaseModel):
    results: list[AutoGooglerResultDTO]
