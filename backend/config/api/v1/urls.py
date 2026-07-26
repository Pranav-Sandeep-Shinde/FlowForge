from django.urls import path ,include
from modules.health.api import urls as health_urls
urlpatterns = [
    path("v1/",include(health_urls))
]