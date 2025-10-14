from django.contrib import admin

from apps.absenteeism.models import AbsenteeismRequest


@admin.register(AbsenteeismRequest)
class AbsenteeismRequestAdmin(admin.ModelAdmin):
    list_display = ("intern", "status", "start_date", "end_date", "submitted_at")
    list_filter = ("status", "start_date", "end_date")
    search_fields = (
        "intern__user__first_name",
        "intern__user__last_name",
        "reason",
    )
