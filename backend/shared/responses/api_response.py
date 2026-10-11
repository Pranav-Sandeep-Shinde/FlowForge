from rest_framework.response import Response
from shared.constants.error_codes import ErrorCode
def success_response(data=None, meta=None,status_code=200):
    
    """
    Returns a standard success response.
    """
    return Response( {
        "success": True,
        "data": data ,
        "meta": meta or {},
        "errors": None
        
    },status=status_code)
    
def error_response(code: ErrorCode, message: str, meta=None, status_code=400, errors=None):
    """
    Returns a standard error response.
    """
    return Response({
        "success": False,
        "data": None,
        "meta": meta or { },
         "errors": [
                {
                    "code": code,
                    "message": message,
                }
            ],
    }, status=status_code)