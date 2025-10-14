from django.contrib import admin

from apps.supervisors.models import EmployeeProfile


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "job_title", "department", "is_clinical_supervisor")
    list_filter = ("department", "is_clinical_supervisor")
    search_fields = ("user__email", "user__first_name", "user__last_name", "department")
