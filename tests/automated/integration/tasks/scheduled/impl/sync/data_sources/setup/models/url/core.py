from pydantic import BaseModel

from src.collectors.enums import URLStatus
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.models.url.data_sources import TestDSURLSetupEntry
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.models.url.source_collector import \
    TestSCURLSetupEntry


class TestURLSetupEntry(BaseModel):
    url: str
    ds_info: TestDSURLSetupEntry | None # Represents URL previously existing in DS DB
    sc_info: TestSCURLSetupEntry | None # Represents URL previously existing in SC DB

    final_url_status: URLStatus
