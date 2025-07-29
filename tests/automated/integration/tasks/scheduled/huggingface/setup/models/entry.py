from pydantic import BaseModel

from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters


class TestURLSetupEntry(BaseModel):
    creation_parameters: TestURLCreationParameters
    picked_up: bool

