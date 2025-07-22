from pydantic import BaseModel, Field


class MuckrockAllFOIARequestsCollectorInputDTO(BaseModel):
    start_page: int = Field(description="The page to start from.", ge=1)
    total_pages: int = Field(description="The total number of pages to fetch.", ge=1, default=1)
