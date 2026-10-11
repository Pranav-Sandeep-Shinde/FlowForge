from shared.exceptions.base import FlowForgeException
from shared.constants.error_codes import ErrorCode
class AuthenticationError(FlowForgeException):
    """
    Exception raised when a user is not authenticated.
    """
    def __init__(self, message: str = "Authentication Error"):
        super().__init__(message=message, code=ErrorCode.UNAUTHORIZED, status_code=401)