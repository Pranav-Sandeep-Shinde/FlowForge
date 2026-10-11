from shared.exceptions.base import FlowForgeException
from shared.constants.error_codes import ErrorCode

def test_flowforge_exception():
    message = "Test exception"
    code = ErrorCode.VALIDATION_ERROR
    status_code = 400

    exception = FlowForgeException(message=message, code=code, status_code=status_code)

    assert exception.message == message
    assert exception.code == code
    assert exception.status_code == status_code
    assert str(exception) == message