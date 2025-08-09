from src.db.models.instantiations.url.core.enums import URLSource

PATCH_ROOT = "src.external.url_request.core.URLProbeManager"
TEST_URL = "https://www.example.com"
TEST_DEST_URL = "https://www.example.com/redirect"
TEST_SOURCE = URLSource.COLLECTOR
