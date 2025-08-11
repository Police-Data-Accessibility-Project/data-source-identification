from pydantic import BaseModel, Field


class AutoGooglerInputDTO(BaseModel):
    urls_per_result: int = Field(
        description="Maximum number of URLs returned per result. Minimum is 1. Default is 10",
        default=10,
        ge=1,
        le=50
    )
    queries: list[str] = Field(
        description="List of queries to search for.",
        min_length=1,
        max_length=100
    )
