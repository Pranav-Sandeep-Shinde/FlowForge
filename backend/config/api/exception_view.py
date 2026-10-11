from rest_framework.views import APIView
from shared.exceptions.not_found import NotFoundError
class TestExceptionView(APIView):
    """
    A view to test exception handling.
    """
    def get(self, request, *args, **kwargs):
        raise NotFoundError("This is a test exception.")
    