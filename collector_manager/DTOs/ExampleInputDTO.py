from pydantic import BaseModel, Field


class ExampleInputDTO(BaseModel):
    example_field: str = Field(description="The example field")
    sleep_time: int = Field(description="The time to sleep, in seconds", default=10)
