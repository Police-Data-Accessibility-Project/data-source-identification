from src.db.models.instantiations.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.templates.markers.bulk.delete import BulkDeletableModel
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class LinkURLAgencyPydantic(
    BulkDeletableModel,
    BulkInsertableModel
):
    url_id: int
    agency_id: int

    @classmethod
    def sa_model(cls) -> type[LinkURLAgency]:
        return LinkURLAgency