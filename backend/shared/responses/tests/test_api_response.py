from shared.constants.error_codes import ErrorCode
from shared.responses.api_response import success_response,error_response

def test_success_response():
    response = success_response(
        data={"id": 1, "name": "Test"},
               meta={"request_id": "abc123"},
               
               status_code=200,
    )

    assert response.status_code == 200
    assert response.data["success"] is True
    assert response.data["data"] == {
        "id": 1,
        "name": "Test",
    }
    assert response.data["meta"] == {"request_id": "abc123"}
    assert response.data["errors"] is None
def test_error_response():
    response = error_response(
        code=ErrorCode.NOT_FOUND,
        message="Workflow not found",
        status_code=404,
    )
    assert response.status_code == 404
    assert response.data["success"] is False
    assert response.data["errors"] == [
        {
            "code": ErrorCode.NOT_FOUND,
            "message": "Workflow not found"
        }
    ]
    assert response.data["meta"] == {}