from src.db.models.helpers import url_id_column
from src.db.models.templates_.standard import StandardBase



class LinkURLRedirectURL(StandardBase):
    __tablename__ = "link_urls_redirect_url"
    source_url_id = url_id_column()
    destination_url_id = url_id_column()

