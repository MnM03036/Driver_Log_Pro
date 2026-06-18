from django.urls import path
from . import views

urlpatterns = [
    path("simulate/", views.simulate_view, name="simulate"),
    path("download-log/", views.download_log_view, name="download-log"),
]
