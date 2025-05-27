from typing import Annotated

from pydantic import BaseModel, Field


class SearchConfig(BaseModel):
    """
    A class that holds the configuration for the AutoGoogler
    Simple now, but might be extended in the future
    """
    urls_per_result: Annotated[
        int,
        "Maximum number of URLs returned per result. Minimum is 1. Default is 10"
    ] = Field(
        default=10,
        ge=1
    )
    queries: Annotated[
        list[str],
        "List of queries to search for."
    ] = Field(
        min_length=1
    )

