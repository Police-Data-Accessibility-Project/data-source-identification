from pydantic import BaseModel, Field


class FinalReviewBaseInfo(BaseModel):
    url_id: int = Field(
        title="The id of the URL."
    )
