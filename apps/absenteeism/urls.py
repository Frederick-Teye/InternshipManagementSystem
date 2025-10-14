from __future__ import annotations

from django.urls import path

from apps.absenteeism import views

app_name = "absenteeism"

urlpatterns = [
    # Intern URLs
    path("request/", views.request_absence, name="request"),
    path("my/", views.my_requests, name="my_requests"),
    path("<int:request_id>/cancel/", views.cancel_request, name="cancel"),
    path("<int:request_id>/view/", views.view_request, name="view"),
    # Supervisor/Manager URLs
    path("pending/", views.pending_requests, name="pending_requests"),
    path("<int:request_id>/approve/", views.approve_request, name="approve"),
    path("list/", views.request_list, name="request_list"),
]
