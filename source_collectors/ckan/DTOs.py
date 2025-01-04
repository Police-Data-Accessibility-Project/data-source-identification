from pydantic import BaseModel, Field


class CKANPackageSearchDTO(BaseModel):
    url: str = Field(description="The package of the CKAN instance.")
    terms: list[str] = Field(description="The search terms to use.")

class GroupAndOrganizationSearchDTO(BaseModel):
    url: str = Field(description="The group or organization of the CKAN instance.")
    ids: list[str] = Field(description="The ids of the group or organization.")

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

