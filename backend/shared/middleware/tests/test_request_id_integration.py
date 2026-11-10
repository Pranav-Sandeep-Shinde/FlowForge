import uuid

from django.urls import reverse
from rest_framework.test import APIClient

from shared.constants.error_codes import ErrorCode


def test_request_id_middleware_integration():
    client = APIClient()

    # Make a real request through Django and DRF.
    response = client.get(reverse("test-exceptions"))

    # Verify that our test endpoint was reached.
    assert response.status_code == 404
    assert response.data["success"] is False
    assert response.data["errors"][0]["code"] == ErrorCode.NOT_FOUND

    # Verify that the middleware added the request ID.
    request_id = response.headers.get("X-Request-ID")
    assert request_id is not None

    # Verify that the ID is a valid UUID4.
    parsed_request_id = uuid.UUID(request_id)
    assert parsed_request_id.version == 4