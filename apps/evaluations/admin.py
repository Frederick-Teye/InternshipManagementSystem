from django.contrib import admin

from apps.evaluations.models import PerformanceAssessment


@admin.register(PerformanceAssessment)
class PerformanceAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "intern",
        "week_number",
        "assessment_date",
        "assessed_by",
        "status",
        "supervisor_score",
        "intern_score",
    )
    list_filter = ("status", "assessment_date")
    search_fields = (
        "intern__user__first_name",
        "intern__user__last_name",
        "assessed_by__user__first_name",
        "assessed_by__user__last_name",
    )
