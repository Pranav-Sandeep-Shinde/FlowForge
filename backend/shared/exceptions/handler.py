from shared.responses import error_response
from shared.exceptions.base import FlowForgeException
from rest_framework.views import exception_handler
def handle_exception(exception: FlowForgeException):
    return error_response(
        message=exception.message,
        code=exception.code,
        status_code=exception.status_code
    )
def custom_exception_handler(exc,context):
    if isinstance(exc, FlowForgeException):
        return handle_exception(exc)
    return exception_handler(exc, context)