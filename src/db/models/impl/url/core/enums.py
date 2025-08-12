from enum import Enum


class URLSource(Enum):
    COLLECTOR = "collector"
    MANUAL = "manual"
    DATA_SOURCES = "data_sources_app"
    REDIRECT = "redirect"
    ROOT_URL = "root_url"