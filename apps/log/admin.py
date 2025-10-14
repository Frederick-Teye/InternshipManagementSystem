from django.contrib import admin

from apps.log.models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "actor", "action", "content_type")
    list_filter = ("action", "timestamp", "content_type")
    search_fields = ("action", "actor__email", "actor__username")
    readonly_fields = (
        "timestamp",
        "actor",
        "action",
        "content_type",
        "object_id",
        "changes",
        "metadata",
        "ip_address",
        "user_agent",
    )
