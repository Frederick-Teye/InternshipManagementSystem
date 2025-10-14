from django.urls import path
from apps.reports import views

app_name = "reports"

urlpatterns = [
    # PDF Reports
    path(
        "intern/<int:intern_id>/download/",
        views.download_intern_report,
        name="download_intern_report",
    ),
    # CSV Exports
    path(
        "attendance/export/",
        views.export_attendance_csv,
        name="export_attendance",
    ),
    path(
        "assessments/export/",
        views.export_assessments_csv,
        name="export_assessments",
    ),
]
