from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from apps.dashboards.views import dashboard
from config.admin_views import log_urls

urlpatterns = [
    path("", lambda request: redirect("accounts:login"), name="home"),
    path("dashboard/", dashboard, name="dashboard"),  # Main dashboard router
    path("admin/", include((log_urls, "admin_logs"), namespace="admin_logs")),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("dashboards/", include("apps.dashboards.urls")),  # Role-specific dashboards
    path("interns/", include("apps.interns.urls")),
    path("attendance/", include("apps.attendance.urls")),
    path("evaluations/", include("apps.evaluations.urls")),
    path("absenteeism/", include("apps.absenteeism.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("reports/", include("apps.reports.urls")),
    # Log views removed - we now write activity and system failures to server log files.
    # path("log/", include("apps.log.urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
