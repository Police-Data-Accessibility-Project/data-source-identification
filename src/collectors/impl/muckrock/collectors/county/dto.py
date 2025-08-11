from pydantic import BaseModel, Field


class MuckrockCountySearchCollectorInputDTO(BaseModel):
    # TODO: How to determine the ID of a parent jurisdiction?
    parent_jurisdiction_id: int = Field(description="The ID of the parent jurisdiction.", ge=1)
    town_names: list[str] = Field(description="The names of the towns to search for.", min_length=1)
