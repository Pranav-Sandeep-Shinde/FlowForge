from shared.exceptions.base import FlowForgeException
from shared.exceptions.conflict import ConflictError
from shared.constants.error_codes import ErrorCode
def test_conflict_error():
    message = "This is a conflict error."
    error = ConflictError(message)

    assert isinstance(error, FlowForgeException)
    assert error.message == message
    assert error.code == ErrorCode.CONFLICT
    assert error.status_code == 409