from shared.exceptions.not_found import NotFoundError
from shared.constants.error_codes import ErrorCode
def test_not_found_error():
    message = "Test not found error"
    exception = NotFoundError(message=message)
    assert str(exception) == message
    assert exception.message == message
    assert exception.code == ErrorCode.NOT_FOUND
    assert exception.status_code == 404
    