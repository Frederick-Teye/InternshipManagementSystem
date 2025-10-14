from __future__ import annotations

from django.urls import path

from apps.notifications import views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_center, name="center"),
    path("<int:notification_id>/read/", views.mark_as_read, name="mark_read"),
    path("mark-all-read/", views.mark_all_as_read, name="mark_all_read"),
    path("api/unread-count/", views.get_unread_count, name="unread_count"),
    path("preferences/", views.notification_preferences, name="preferences"),
]
