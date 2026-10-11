from django.urls import reverse
from rest_framework.test import APIClient

from shared.constants.error_codes import ErrorCode


def test_flowforge_exception_handler_integration():
    client = APIClient()

    url = reverse("test-exceptions")
    response = client.get(url)

    assert response.status_code == 404
    assert response.data["success"] is False
    assert response.data["data"] is None
    assert response.data["meta"] == {}
    assert response.data["errors"][0]["code"] == ErrorCode.NOT_FOUND
    assert response.data["errors"][0]["message"] == "This is a test exception."