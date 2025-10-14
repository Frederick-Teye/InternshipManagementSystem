from __future__ import annotations

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from apps.dashboards.views import dashboard

urlpatterns = [
    path("", lambda request: redirect("accounts:login"), name="home"),
    path("dashboard/", dashboard, name="dashboard"),  # Main dashboard router
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("dashboards/", include("apps.dashboards.urls")),  # Role-specific dashboards
    path("interns/", include("apps.interns.urls")),
    path("attendance/", include("apps.attendance.urls")),
    path("evaluations/", include("apps.evaluations.urls")),
    path("absenteeism/", include("apps.absenteeism.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("reports/", include("apps.reports.urls")),
]
