from shared.constants.error_codes import ErrorCode
class FlowForgeException(Exception):
    """
    Base class for all FlowForge exceptions.
    """
    def __init__(self,message:str,code:ErrorCode,status_code:int):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code