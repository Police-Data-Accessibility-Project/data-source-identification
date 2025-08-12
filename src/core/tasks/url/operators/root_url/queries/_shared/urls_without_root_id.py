"""
A query to retrieve URLS that either
- are not a root URL
- are not already linked to a root URL

"""

from sqlalchemy import select

from src.db.models.impl.flag.root_url.sqlalchemy import FlagRootURL
from src.db.models.impl.link.urls_root_url.sqlalchemy import LinkURLRootURL
from src.db.models.impl.url.core.sqlalchemy import URL

URLS_WITHOUT_ROOT_ID_QUERY = (
    select(
        URL.id,
        URL.url
    ).outerjoin(
        FlagRootURL,
        URL.id == FlagRootURL.url_id
    ).outerjoin(
        LinkURLRootURL,
        URL.id == LinkURLRootURL.url_id
    ).where(
        FlagRootURL.url_id.is_(None),
        LinkURLRootURL.url_id.is_(None)
    )
)