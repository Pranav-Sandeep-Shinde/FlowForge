from django.urls import include, path

urlpatterns = [
    path("executions/", include("modules.executions.api.urls")),
    path("health/", include("modules.health.api.urls")),
    path("identity/", include("modules.identity.api.urls")),
    path("notifications/", include("modules.notifications.api.urls")),
    path("organizations/", include("modules.organizations.api.urls")),
    path("workflows/", include("modules.workflows.api.urls")),
]
