from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.HealthCheckView.as_view(), name="health-check"),
    path("ask/", views.AskView.as_view(), name="copilot-ask"),
    path("moderate-image/", views.moderate_image, name="moderate-image"),
]
