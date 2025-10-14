from django.contrib import admin

from apps.attendance.models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "intern",
        "branch",
        "check_in_time",
        "approval_status",
        "auto_approved",
    )
    list_filter = ("approval_status", "auto_approved", "branch")
    search_fields = (
        "intern__user__first_name",
        "intern__user__last_name",
        "branch__name",
    )
