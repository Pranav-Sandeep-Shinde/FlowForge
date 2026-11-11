import uuid
from django.http import HttpResponse
from django.test import RequestFactory,TestCase
from shared.middleware.request_id import RequestIDMiddleware
def test_request_id_middleware():
    request = RequestFactory().get("/")
    middleware = RequestIDMiddleware(
        lambda request:HttpResponse("OK")
    )#This will execute the init 
    response = middleware(request) #This will call the __call__ method 
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"] == request.request_id
    assert type(uuid.uuid4()) == type(uuid.UUID(response.headers["X-Request-ID"]))
    request_id = uuid.UUID(response.headers["X-Request-ID"])
    assert request_id.version == 4