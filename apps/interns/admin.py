from django.contrib import admin

from apps.interns.models import InternProfile, InternType


@admin.register(InternType)
class InternTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "display_name")
    search_fields = ("name", "display_name")


@admin.register(InternProfile)
class InternProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "school",
        "branch",
        "internal_supervisor",
        "intern_type",
        "start_date",
        "end_date",
    )
    list_filter = ("intern_type", "branch", "school")
    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "school__name",
    )
