import uuid
from shared.logging.context import request_id_var

class RequestIDMiddleware:
    """
    Middleware that assigns a unique ID to each incoming request
    for tracking and logging purposes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        request_id = str(uuid.uuid4())
        token = request_id_var.set(request_id)
        try:
            request.request_id = request_id
            response = self.get_response(request)
            response["X-Request-ID"] = request_id
            return response
        finally:
            # Ensure that the request ID is reset even if an exception occurs
            request_id_var.reset(token)
