from pydantic import BaseModel, Field


class MuckrockSimpleSearchCollectorInputDTO(BaseModel):
    search_string: str = Field(description="The search string to use.")
    max_results: int or None = Field(
        description="The maximum number of results to return. "
                    "If none, all results will be returned (and may take considerably longer to process).",
        ge=1,
        default=10
    )
