from __future__ import annotations

from django.urls import path

from apps.log.views import (
    activity_log_list,
    user_activity_log,
    my_activity_log,
    clear_activity_logs,
)

app_name = "log"

urlpatterns = [
    # Admin views
    path("admin/", activity_log_list, name="activity_log_list"),
    path("admin/clear/", clear_activity_logs, name="clear_activity_logs"),
    # Supervisor views
    path("supervisor/", user_activity_log, name="supervisor_activity_log"),
    path("supervisor/user/<int:user_id>/", user_activity_log, name="user_activity_log"),
    # User views
    path("my/", my_activity_log, name="my_activity_log"),
]
