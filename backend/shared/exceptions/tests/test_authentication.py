from shared.constants.error_codes import ErrorCode
from shared.exceptions.authentication import AuthenticationError
from shared.exceptions.base import FlowForgeException
def test_authentication_error():
    message = "User not authenticated"
    error = AuthenticationError(message=message)
    assert isinstance(error,FlowForgeException)
    assert error.message == message
    assert error.code == ErrorCode.UNAUTHORIZED
    assert error.status_code == 401
