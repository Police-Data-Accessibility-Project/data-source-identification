from pydantic import BaseModel, Field


class MuckrockSimpleSearchCollectorInputDTO(BaseModel):
    search_string: str = Field(description="The search string to use.")
    max_results: int or None = Field(
        description="The maximum number of results to return. "
                    "If none, all results will be returned (and may take considerably longer to process).",
        ge=1,
        default=10
    )

class MuckrockCountySearchCollectorInputDTO(BaseModel):
    # TODO: How to determine the ID of a parent jurisdiction?
    parent_jurisdiction_id: int = Field(description="The ID of the parent jurisdiction.", ge=1)
    town_names: list[str] = Field(description="The names of the towns to search for.", min_length=1)

class MuckrockAllFOIARequestsCollectorInputDTO(BaseModel):
    start_page: int = Field(description="The page to start from.", ge=1)
    total_pages: int = Field(description="The total number of pages to fetch.", ge=1, default=1)