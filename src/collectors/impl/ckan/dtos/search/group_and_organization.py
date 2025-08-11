from typing import Optional

from pydantic import BaseModel, Field

from src.collectors.impl.ckan.dtos.search._helpers import url_field


class GroupAndOrganizationSearchDTO(BaseModel):
    url: str = url_field
    ids: Optional[list[str]] = Field(
        description="The ids of the group or organization to get packages from."
    )
