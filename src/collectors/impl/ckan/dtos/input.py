from pydantic import BaseModel, Field

from src.collectors.impl.ckan.dtos.search.group_and_organization import GroupAndOrganizationSearchDTO
from src.collectors.impl.ckan.dtos.search.package import CKANPackageSearchDTO


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
