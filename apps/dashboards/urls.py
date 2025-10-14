from __future__ import annotations

from django.urls import path

from apps.dashboards.views import (
    dashboard,
    admin_dashboard,
    employee_dashboard,
    intern_dashboard,
    manager_dashboard,
    supervisor_dashboard,
)

app_name = "dashboards"

urlpatterns = [
    path("", dashboard, name="dashboard"),  # Main dashboard router
    path("intern/", intern_dashboard, name="intern"),
    path("supervisor/", supervisor_dashboard, name="supervisor"),
    path("manager/", manager_dashboard, name="manager"),
    path("admin/", admin_dashboard, name="admin"),
    path("employee/", employee_dashboard, name="employee"),
]
