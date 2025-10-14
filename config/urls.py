from __future__ import annotations

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("", lambda request: redirect("accounts:login"), name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("dashboard/", include("apps.dashboards.urls")),
    path("attendance/", include("apps.attendance.urls")),
    path("evaluations/", include("apps.evaluations.urls")),
    path("absenteeism/", include("apps.absenteeism.urls")),
]
