from pydantic import BaseModel

from tests.automated.unit.db.utils.validate.mock.protocol import MockProtocol


class MockClassNoProtocol(BaseModel):
    mock_attribute: str | None = None

class MockClassWithProtocol(BaseModel, MockProtocol):
    mock_attribute: str | None = None