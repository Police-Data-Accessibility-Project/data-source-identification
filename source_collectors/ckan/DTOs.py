from typing import Optional

from pydantic import BaseModel, Field

url_field = Field(description="The base CKAN URL to search from.")

class CKANPackageSearchDTO(BaseModel):
    url: str = url_field
    terms: Optional[list[str]] = Field(
        description="The search terms to use to refine the packages returned. "
                    "None will return all packages.",
        default=None
    )

class GroupAndOrganizationSearchDTO(BaseModel):
    url: str = url_field
    ids: Optional[list[str]] = Field(
        description="The ids of the group or organization to get packages from."
    )

class CKANInputDTO(BaseModel):
    package_search: list[CKANPackageSearchDTO] or None = Field(
        description="The list of package searches to perform.",
        default=None
    )
    group_search: list[GroupAndOrganizationSearchDTO] or None = Field(
        description="The list of group searches to perform.",
        default=None
    )
    organization_search: list[GroupAndOrganizationSearchDTO] or None = Field(
        description="The list of organization searches to perform.",
        default=None
    )

