from shared.constants.error_codes import ErrorCode
from shared.exceptions.not_found import NotFoundError
from shared.exceptions.handler import custom_exception_handler
from rest_framework.exceptions import NotFound
def test_flowforge_exception_handler():
    exception = NotFoundError("Workflow not found")

    response = custom_exception_handler(exception, {})

    assert response.status_code == 404
    assert response.data["success"] is False
    assert response.data["errors"][0]["code"] == ErrorCode.NOT_FOUND
    assert response.data["errors"][0]["message"] == "Workflow not found"
def test_drf_exception_handler():
    exception = NotFound()

    response = custom_exception_handler(exception, {})

    assert response.status_code == 404
def test_handler():
    test_flowforge_exception_handler()
    test_drf_exception_handler()
    