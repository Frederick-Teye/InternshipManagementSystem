from __future__ import annotations

from django.urls import path

from apps.attendance.views import (
    approve_attendance,
    attendance_list,
    checkout,
    mark_attendance,
    my_attendance,
    pending_approvals,
)

app_name = "attendance"

urlpatterns = [
    # Intern views
    path("mark/", mark_attendance, name="mark"),
    path("my/", my_attendance, name="my_attendance"),
    path("<int:attendance_id>/checkout/", checkout, name="checkout"),
    # Supervisor/Manager views
    path("pending/", pending_approvals, name="pending_approvals"),
    path("<int:attendance_id>/approve/", approve_attendance, name="approve"),
    path("list/", attendance_list, name="list"),
]
