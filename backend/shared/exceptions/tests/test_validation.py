from shared.exceptions.validation_error import ValidationError
from shared.constants.error_codes import ErrorCode
def test_validation_error():
    message = "Invalid input."

    exception = ValidationError(message)

    assert str(exception) == message
    assert exception.message == message
    assert exception.code == ErrorCode.VALIDATION_ERROR
    assert exception.status_code == 400