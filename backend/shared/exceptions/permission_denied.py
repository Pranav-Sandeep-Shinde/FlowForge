from shared.constants.error_codes import ErrorCode
from shared.exceptions.base import FlowForgeException


class PermissionDeniedError(FlowForgeException):
    """Raised when an operation is not permitted."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, code=ErrorCode.FORBIDDEN, status_code=403)
