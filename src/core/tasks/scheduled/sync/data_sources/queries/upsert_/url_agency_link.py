from src.db.models.instantiations.link.url_agency.pydantic import LinkURLAgencyUpsertModel
from src.db.queries.base.builder import QueryBuilderBase


class URLAgencyLinkUpsertQueryBuilder(QueryBuilderBase):

    def __init__(self, models: list[LinkURLAgencyUpsertModel]):
        super().__init__()
        self.models = models