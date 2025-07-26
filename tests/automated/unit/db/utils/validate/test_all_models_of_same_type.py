import pytest

from src.db.utils.validate import validate_all_models_of_same_type
from tests.automated.unit.db.utils.validate.mock.class_ import MockClassNoProtocol, MockClassWithProtocol


def test_validate_all_models_of_same_type_happy_path():

    models = [MockClassNoProtocol() for _ in range(3)]
    validate_all_models_of_same_type(models)

def test_validate_all_models_of_same_type_error_path():

    models = [MockClassNoProtocol() for _ in range(2)]
    models.append(MockClassWithProtocol())
    with pytest.raises(TypeError):
        validate_all_models_of_same_type(models)