from django.urls import include, path
from config.api.exception_view import TestExceptionView

urlpatterns = [
    path("executions/", include("modules.executions.api.urls")),
    path("health/", include("modules.health.api.urls")),
    path("identity/", include("modules.identity.api.urls")),
    path("notifications/", include("modules.notifications.api.urls")),
    path("organizations/", include("modules.organizations.api.urls")),
    path("workflows/", include("modules.workflows.api.urls")),
    path("test-exceptions/", TestExceptionView.as_view(), name="test-exceptions"),
]
