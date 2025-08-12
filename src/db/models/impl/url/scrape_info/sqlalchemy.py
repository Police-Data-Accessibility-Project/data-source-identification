from src.db.models.helpers import enum_column
from src.db.models.impl.url.scrape_info.enums import ScrapeStatus
from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.standard import StandardBase


class URLScrapeInfo(
    StandardBase,
    URLDependentMixin
):

    __tablename__ = 'url_scrape_info'

    status = enum_column(
        enum_type=ScrapeStatus,
        name='scrape_status',
    )