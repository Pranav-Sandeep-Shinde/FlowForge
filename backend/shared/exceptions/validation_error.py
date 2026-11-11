from shared.exceptions.base import FlowForgeException
from shared.constants.error_codes import ErrorCode
class ValidationError(FlowForgeException):
    """Raised when a validation error occurs."""

    def __init__(self,message:str,code:ErrorCode=ErrorCode.VALIDATION_ERROR,status_code:int=400):
        super().__init__(message=message, code=code, status_code=400)