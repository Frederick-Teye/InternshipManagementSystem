from django.urls import path
from apps.reports import views

app_name = "reports"

urlpatterns = [
    # PDF Reports - Keep only the intern performance report that works
    path(
        "intern/<int:intern_id>/download/",
        views.download_intern_report,
        name="download_intern_report",
    ),
]
