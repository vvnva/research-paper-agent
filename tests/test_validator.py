from app.core.config import Settings
from app.core.errors import ValidationError
from app.modules.validator import InputValidator


def test_validator_accepts_normal_query():
    validator = InputValidator(Settings(MIN_QUERY_LEN=5))
    assert validator.validate(" graph neural networks ") == "graph neural networks"


def test_validator_rejects_short_query():
    validator = InputValidator(Settings(MIN_QUERY_LEN=5))
    try:
        validator.validate("abc")
    except ValidationError:
        assert True
        return
    assert False, "expected ValidationError"
