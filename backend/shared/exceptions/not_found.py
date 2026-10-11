from shared.exceptions.base import FlowForgeException
from shared.constants.error_codes import ErrorCode
class NotFoundError(FlowForgeException):
    """
    Exception raised when a requested resource is not found.
    """
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, code=ErrorCode.NOT_FOUND, status_code=404)