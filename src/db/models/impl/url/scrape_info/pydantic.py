from src.db.models.impl.url.scrape_info.enums import ScrapeStatus
from src.db.models.impl.url.scrape_info.sqlalchemy import URLScrapeInfo
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLScrapeInfoInsertModel(BulkInsertableModel):
    url_id: int
    status: ScrapeStatus

    @classmethod
    def sa_model(cls) -> type[Base]:
        return URLScrapeInfo