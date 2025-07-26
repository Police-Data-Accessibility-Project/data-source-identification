import pytest

from src.db.utils.validate import validate_has_protocol
from tests.automated.unit.db.utils.validate.mock.class_ import MockClassWithProtocol, MockClassNoProtocol
from tests.automated.unit.db.utils.validate.mock.protocol import MockProtocol


def test_validate_has_protocol_happy_path():

    model = MockClassWithProtocol()
    validate_has_protocol(model, MockProtocol)

def test_validate_has_protocol_error_path():

    model = MockClassNoProtocol()
    with pytest.raises(TypeError):
        validate_has_protocol(model, MockProtocol)