from shared.constants.error_codes import ErrorCode
from shared.exceptions.permission_denied import PermissionDeniedError


def test_permission_denied_error():
    message = "You do not have permission to modify this workflow."

    exception = PermissionDeniedError(message)

    assert exception.message == message
    assert str(exception) == message
    assert exception.code == ErrorCode.FORBIDDEN
    assert exception.status_code == 403
