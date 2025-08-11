from typing import Optional

from pydantic import BaseModel, Field

from src.collectors.impl.ckan.dtos.search._helpers import url_field


class CKANPackageSearchDTO(BaseModel):
    url: str = url_field
    terms: Optional[list[str]] = Field(
        description="The search terms to use to refine the packages returned. "
                    "None will return all packages.",
        default=None
    )
