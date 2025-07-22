from pydantic import BaseModel, Field


class GoogleSearchQueryResultsInnerDTO(BaseModel):
    url: str = Field(description="The URL of the result.")
    title: str = Field(description="The title of the result.")
    snippet: str = Field(description="The snippet of the result.")
