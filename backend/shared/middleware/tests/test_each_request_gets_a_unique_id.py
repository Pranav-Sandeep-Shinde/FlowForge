from django.http import HttpResponse
from django.test import RequestFactory,TestCase
from shared.middleware.request_id import RequestIDMiddleware
def test_each_request_gets_a_unique_id():
    request1 = RequestFactory().get("/")
    request2 = RequestFactory().get("/")

    middleware = RequestIDMiddleware(
        lambda request: HttpResponse("OK")
    )

    response1 = middleware(request1)
    response2 = middleware(request2)

    assert (
        response1.headers["X-Request-ID"]
        != response2.headers["X-Request-ID"]
    )