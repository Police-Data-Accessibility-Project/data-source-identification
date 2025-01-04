from pydantic import BaseModel, Field


class CommonCrawlerInputDTO(BaseModel):
    common_crawl_id: str = Field(
        description="The Common Crawl ID to use.",
        default="CC-MAIN-2024-51"
    )
    url: str = Field(description="The URL to query", default="*.gov")
    search_term: str = Field(description="The keyword to search in the url", default="police")
    start_page: int = Field(description="The page to start from", default=1)
    total_pages: int = Field(description="The total number of pages to fetch", default=1)