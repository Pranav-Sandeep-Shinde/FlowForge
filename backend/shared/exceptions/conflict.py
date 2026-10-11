from shared.exceptions.base import FlowForgeException
from shared.constants.error_codes import ErrorCode
class ConflictError(FlowForgeException):
    """Raised when a conflict error occurs."""

    def __init__(self,message:str,code:ErrorCode=ErrorCode.CONFLICT,status_code:int=409):
        super().__init__(message=message, code=code, status_code=409)