from pydantic import BaseModel

from tests.automated.integration.tasks.url.html.setup.models.entry import TestURLHTMLTaskSetupEntry


class TestURLHTMLTaskSetupRecord(BaseModel):
    url_id: int
    entry: TestURLHTMLTaskSetupEntry